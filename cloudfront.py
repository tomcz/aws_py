from properties import loadcredentials
import time, httplib, xml.dom.minidom

DEFAULT_HOST = 'cloudfront.amazonaws.com'

class CommonParameters:
    def __init__(self, method, headers={}):
        self.method = method
        self.headers = headers

    def setAuthHeader(self, credentials):
        value = 'AWS ' + credentials.access_key_id + ':' + credentials.sign(self.textToSign())
        self.headers['Authorization'] = value

    def textToSign(self):
        self.headers['Date'] = time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime())
        return self.headers['Date']

    def createPath(self):
        pass

def send_request(parameters, request_body=None):
    print '****************'
    print '* REQUEST      *'
    print '****************'

    print '%s https://%s%s' % (parameters.method, DEFAULT_HOST, parameters.createPath())

    if request_body:
        print request_body

    print '****************'
    print '* RESPONSE     *'
    print '****************'

    parameters.setAuthHeader(loadcredentials())
    conn = httplib.HTTPSConnection(DEFAULT_HOST)
    try:
        conn.putrequest(parameters.method, parameters.createPath())

        for name, value in parameters.headers.iteritems():
            conn.putheader(name, value)

        conn.endheaders()

        if request_body:
            conn.send(request_body)

        response = conn.getresponse()
        print response.status, response.getheaders()

        response_dom = xml.dom.minidom.parseString(response.read())
        print response_dom.toprettyxml()

    finally:
        conn.close()
