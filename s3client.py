import urllib, httplib, time, hashlib, base64, os, mimetypes
from BeautifulSoup import BeautifulStoneSoup
from properties import loadcredentials

CHUNK_SIZE = 4096

DEFAULT_HOST = "s3.amazonaws.com"
INSECURE_PROTOCOL = "http"
SECURE_PROTOCOL = "https"

DATE_HEADER = "date"
CONTENT_MD5_HEADER = "content-md5"
CONTENT_TYPE_HEADER = "content-type"
ALTERNATIVE_DATE_HEADER = "x-amz-date"
AMAZON_HEADER_PREFIX = "x-amz-"

VIDEO_CONTENT_TYPES = {'.ogv': 'video/ogg', '.mp4': 'video/mp4', '.webm': 'video/webm'}

class Parameters:
    def __init__(self, method, bucket_name=None, object_key=None, headers={}, sub_resource=None, expires=None):
        self.method = method
        self.bucket_name = bucket_name
        self.object_key = object_key
        self.headers = headers
        self.sub_resource = sub_resource
        self.expires = expires

    def setAuthHeader(self, credentials):
        value = "AWS " + credentials.access_key_id + ":" + credentials.sign(self.textToSign())
        self.headers['Authorization'] = value

    def textToSign(self):
        if not 'Date' in self.headers:
            self.headers['Date'] = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())

        canonical_headers = self.canonicalHeaders()
        canonical_header_keys = canonical_headers.keys()
        canonical_header_keys.sort()

        result = self.method + '\n'

        for header in canonical_header_keys:
            if header.startswith(AMAZON_HEADER_PREFIX):
                result += header + ':' + canonical_headers[header]
            else:
                result += canonical_headers[header]
            result += '\n'

        return result + self.createPath()

    def canonicalHeaders(self):
        result = {}

        for key, value in self.headers.iteritems():
            header_name = key.lower()
            if self.isCanonicalHeader(header_name):
                result[header_name] = value

        if ALTERNATIVE_DATE_HEADER in result:
            result[DATE_HEADER] = ''

        if self.expires:
            result[DATE_HEADER] = str(self.expires)

        if not CONTENT_TYPE_HEADER in result:
            result[CONTENT_TYPE_HEADER] = ''

        if not CONTENT_MD5_HEADER in result:
            result[CONTENT_MD5_HEADER] = ''

        if not DATE_HEADER in result:
            raise Exception, "Must have a date header"

        return result

    def isCanonicalHeader(self, name):
        return name == CONTENT_TYPE_HEADER or\
               name == CONTENT_MD5_HEADER or\
               name == DATE_HEADER or\
               name.startswith(AMAZON_HEADER_PREFIX)

    def not_empty(self, value):
        return value and len(value) > 0

    def createPath(self, use_vhost=False):
        path = '/'
        if not use_vhost and self.not_empty(self.bucket_name):
            path += self.bucket_name + "/"
        if self.not_empty(self.object_key):
            path += urllib.quote_plus(self.object_key, '/')
        if self.not_empty(self.sub_resource):
            path += '?' + self.sub_resource
        return path

    def hostname(self, use_vhost=False):
        if use_vhost and self.not_empty(self.bucket_name):
            return self.bucket_name + '.' + DEFAULT_HOST
        else:
            return DEFAULT_HOST

class S3Client:
    def __init__(self, credentials, use_https=True, use_vhost=True):
        self.credentials = credentials
        self.use_https = use_https
        self.use_vhost = use_vhost

    def listBuckets(self):
        params = Parameters('GET')
        return self.process(params, lambda conn: self.parseBuckets(conn.getresponse()))

    def bucketExists(self, bucket_name):
        params = Parameters('HEAD', bucket_name)
        return self.process(params, lambda conn: conn.getresponse().status != httplib.NOT_FOUND)

    def createBucket(self, bucket_name):
        params = Parameters('PUT', bucket_name)
        self.process(params, lambda conn: self.expect(conn.getresponse(), httplib.OK))

    def deleteBucket(self, bucket_name):
        params = Parameters('DELETE', bucket_name)
        self.process(params, lambda conn: self.expect(conn.getresponse(), httplib.NO_CONTENT))

    def listObjects(self, bucket_name):
        params = Parameters('GET', bucket_name)
        return self.process(params, lambda conn: self.parseObjects(conn.getresponse()))

    def objectExists(self, bucket_name, object_key):
        params = Parameters('HEAD', bucket_name, object_key)
        return self.process(params, lambda conn: conn.getresponse().status == httplib.OK)

    def createObject(self, bucket_name, object_key, file_path):
        headers = {
            'Content-Length': str(os.path.getsize(file_path)),
            'Content-Type': self.getMimeType(file_path),
            'Content-MD5': self.computeMD5(file_path)
        }
        params = Parameters('PUT', bucket_name, object_key, headers)
        self.process(params, lambda conn: self.sendFile(conn, file_path))

    def downloadObject(self, bucket_name, object_key, file_path):
        params = Parameters('GET', bucket_name, object_key)
        self.process(params, lambda conn: self.receiveFile(conn.getresponse(), file_path))

    def publicURL(self, bucket_name, object_key, expires_datetime):
        expires = int(time.mktime(expires_datetime.timetuple()))
        params = Parameters('GET', bucket_name, object_key, {}, None, expires)
        signature = self.credentials.sign(params.textToSign())
        query = [
            ('AWSAccessKeyId', self.credentials.access_key_id),
            ('Expires', str(expires)),
            ('Signature', signature)
        ]
        if self.use_https:
            protocol = SECURE_PROTOCOL
        else:
            protocol = INSECURE_PROTOCOL
        return protocol + '://' +\
               params.hostname(self.use_vhost) +\
               params.createPath(self.use_vhost) +\
               "?" + urllib.urlencode(query)

    def deleteObject(self, bucket_name, object_key):
        params = Parameters('DELETE', bucket_name, object_key)
        self.process(params, lambda conn: self.expect(conn.getresponse(), httplib.NO_CONTENT))

    def process(self, params, callback):
        params.setAuthHeader(self.credentials)
        if self.use_https:
            conn = httplib.HTTPSConnection(params.hostname(self.use_vhost))
        else:
            conn = httplib.HTTPConnection(params.hostname(self.use_vhost))
        try:
            conn.putrequest(params.method, params.createPath(self.use_vhost))
            for name, value in params.headers.iteritems():
                conn.putheader(name, value)
            conn.endheaders()
            return callback(conn)
        finally:
            conn.close()

    def sendFile(self, conn, file_path):
        with open(file_path, 'rb') as src:
            self.copy(src.read, conn.send)
        response = conn.getresponse()
        self.expect(response, httplib.OK)

    def receiveFile(self, response, file_path):
        self.expect(response, httplib.OK)
        with open(file_path, 'wb') as dest:
            self.copy(response.read, dest.write)

    def parseBuckets(self, response):
        self.expect(response, httplib.OK)
        result = []
        dom = BeautifulStoneSoup(response.read())
        for element in dom.findAll('bucket'):
            result.append(element.find('name').string)
        return result

    def parseObjects(self, response):
        self.expect(response, httplib.OK)
        result = []
        dom = BeautifulStoneSoup(response.read())
        for element in dom.findAll('contents'):
            name = element.find('key').string
            size = element.find('size').string
            last_modified = element.find('lastmodified').string
            result.append(S3Object(name, size, last_modified))
        return result

    def expect(self, response, expected):
        if response.status != expected:
            message = "Expected [%s], actual [%s]" % (str(expected), str(response.status))
            raise BadHttpResponse, message

    def getMimeType(self, file_path):
        basename = os.path.basename(file_path)
        name, ext = os.path.splitext(basename)
        if ext in VIDEO_CONTENT_TYPES:
            return VIDEO_CONTENT_TYPES[ext]
        else:
            type, encoding = mimetypes.guess_type(basename, False)
            return type if type else 'application/octet-stream'

    def computeMD5(self, file_path):
        md5 = hashlib.md5()
        with open(file_path, 'rb') as src:
            self.copy(src.read, md5.update)
        digest = md5.digest()
        return base64.b64encode(digest)

    def copy(self, input, output):
        buf = input(CHUNK_SIZE)
        while len(buf) > 0:
            output(buf)
            buf = input(CHUNK_SIZE)

class BadHttpResponse(Exception):
    """Raised when an unexpected status code is returned"""
    pass

class S3Object:
    def __init__(self, name, size, last_modified):
        self.last_modified = last_modified
        self.size = size
        self.name = name

    def describe(self):
        return self.name, self.size, self.last_modified

    def __str__(self):
        return '%s -- %s bytes -- %s' % self.describe()

if __name__ == '__main__':
    client = S3Client(loadcredentials())
    for bucket_name in client.listBuckets():
        print "\nBucket:", bucket_name
        for object in client.listObjects(bucket_name):
            print "Object:", object
