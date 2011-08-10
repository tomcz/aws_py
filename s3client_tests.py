from s3client import Parameters, S3Client, BadHttpResponse
import unittest, os, tempfile, datetime, urllib, uuid
from properties import Credentials, loadcredentials

class CredentialsTests(unittest.TestCase):
    def testCreatesExpectedSignature(self):
        credentials = Credentials("test", "uV3F3YluFJax1cknvbcGwgjvx4QpvB+leU8dUj2o")
        textToSign = "GET\n\n\nTue, 27 Mar 2007 19:36:42 +0000\n/johnsmith/photos/puppy.jpg"
        self.assertEqual("xXjDGYUmKxnwqr5KXNPGldn5LbA=", credentials.sign(textToSign))

class ParametersTests(unittest.TestCase):
    def testCreatesExpectedStringForObjectGet(self):
        headers = {"Date": "Tue, 27 Mar 2007 19:36:42 +0000"}
        params = Parameters('GET', 'johnsmith', 'puppy.jpg', headers)
        expected = "GET\n\n\nTue, 27 Mar 2007 19:36:42 +0000\n/johnsmith/puppy.jpg"
        self.assertEqual(expected, params.textToSign())

    def testCreatesExpectedStringForObjectGetWithPath(self):
        headers = {"Date": "Tue, 27 Mar 2007 19:36:42 +0000"}
        params = Parameters('GET', 'johnsmith', 'cute/puppy.jpg', headers)
        expected = "GET\n\n\nTue, 27 Mar 2007 19:36:42 +0000\n/johnsmith/cute/puppy.jpg"
        self.assertEqual(expected, params.textToSign())

    def testCreatesExpectedStringForObjectPut(self):
        headers = {
            "Date": "Tue, 27 Mar 2007 21:15:45 +0000",
            "Content-MD5": "4gJE4saaMU4BqNR0kLY+lw==",
            "Content-Type": "image/jpeg",
            "Content-Length": "94328"
        }
        params = Parameters('PUT', 'johnsmith', 'puppy.jpg', headers)
        expected = "PUT\n4gJE4saaMU4BqNR0kLY+lw==\nimage/jpeg\nTue, 27 Mar 2007 21:15:45 +0000\n/johnsmith/puppy.jpg"
        self.assertEqual(expected, params.textToSign())

    def testCreatesExpectedStringForBucketList(self):
        headers = {"Date": "Tue, 27 Mar 2007 19:36:42 +0000"}
        params = Parameters('GET', 'johnsmith', None, headers)
        expected = "GET\n\n\nTue, 27 Mar 2007 19:36:42 +0000\n/johnsmith/"
        self.assertEqual(expected, params.textToSign())

    def testCreatesExpectedStringForAclFetch(self):
        headers = {"Date": "Tue, 27 Mar 2007 19:36:42 +0000"}
        params = Parameters('GET', 'johnsmith', None, headers, 'acl')
        expected = "GET\n\n\nTue, 27 Mar 2007 19:36:42 +0000\n/johnsmith/?acl"
        self.assertEqual(expected, params.textToSign())

    def testCreatesExpectedStringForObjectDeleteWithDateAlternative(self):
        headers = {
            "Date": "Tue, 27 Mar 2007 21:15:45 +0000",
            "x-amz-date": "Tue, 27 Mar 2007 21:20:26 +0000"
        }
        params = Parameters("DELETE", "johnsmith", "puppy.jpg", headers)
        expected = "DELETE\n\n\n\nx-amz-date:Tue, 27 Mar 2007 21:20:26 +0000\n/johnsmith/puppy.jpg"
        self.assertEqual(expected, params.textToSign())

    def testCreatesExpectedStringForObjectGetWithExpiryTimestamp(self):
        headers = {"Date": "Tue, 27 Mar 2007 19:36:42 +0000"}
        params = Parameters("GET", "johnsmith", "puppy.jpg", headers, None, 1211233765000)
        expected = "GET\n\n\n1211233765000\n/johnsmith/puppy.jpg"
        self.assertEqual(expected, params.textToSign())

    def testCreatesExpectedAuthHeader(self):
        credentials = Credentials("0PN5J17HBGZHT7JJ3X82", "uV3F3YluFJax1cknvbcGwgjvx4QpvB+leU8dUj2o")

        headers = {"Date": "Tue, 27 Mar 2007 19:36:42 +0000"}
        params = Parameters('GET', 'johnsmith', 'photos/puppy.jpg', headers)
        params.setAuthHeader(credentials)

        expectedHeader = "AWS 0PN5J17HBGZHT7JJ3X82:xXjDGYUmKxnwqr5KXNPGldn5LbA="
        self.assertEqual(expectedHeader, params.headers['Authorization'])

class S3ClientTests(unittest.TestCase):
    def testShouldFindPublicBuckets(self):
        client = S3Client(loadcredentials())
        self.failUnless(client.bucketExists('public'))
        self.failUnless(client.bucketExists('Public'))

    def testShouldCreateAndDeleteBucket(self):
        client = S3Client(loadcredentials())
        bucket_name = "test-" + str(uuid.uuid4())

        client.createBucket(bucket_name)
        self.failUnless(client.bucketExists(bucket_name))

        bucket_list = client.listBuckets()
        self.failUnless(len(bucket_list) > 0)
        self.failUnless(bucket_name in bucket_list)

        client.deleteBucket(bucket_name)
        self.failIf(client.bucketExists(bucket_name))

    def testShouldReturnOctetStreamForUnknownFileType(self):
        client = S3Client(loadcredentials())
        self.assertEqual('application/octet-stream', client.getMimeType('/foo/file.foo'))

    def testShouldReturnPdfMimieTypeForPdfFile(self):
        client = S3Client(loadcredentials())
        self.assertEqual('application/pdf', client.getMimeType('/foo/file.pdf'))

    def testShouldCreateAndDeleteObjectInBucket(self):
        client = S3Client(loadcredentials())

        bucket_name = "test-" + str(uuid.uuid4())
        client.createBucket(bucket_name)

        object_key = 's3client.py'
        file_path = os.path.join(os.getcwd(), object_key)
        client.createObject(bucket_name, object_key, file_path)

        self.failUnless(client.objectExists(bucket_name, object_key))

        client.deleteObject(bucket_name, object_key)
        self.failIf(client.objectExists(bucket_name, object_key))

        client.deleteBucket(bucket_name)

    def testCannotDeleteBucketWithObject(self):
        client = S3Client(loadcredentials())

        bucket_name = "test-" + str(uuid.uuid4())
        client.createBucket(bucket_name)

        object_key = 's3client.py'
        file_path = os.path.join(os.getcwd(), object_key)
        client.createObject(bucket_name, object_key, file_path)

        try:
            client.deleteBucket(bucket_name)
            self.fail('Should have failed to delete a bucket with an object')
        except BadHttpResponse:
            pass

        client.deleteObject(bucket_name, object_key)
        client.deleteBucket(bucket_name)

    def testCanDownloadUploadedFile(self):
        client = S3Client(loadcredentials())

        bucket_name = "test-" + str(uuid.uuid4())
        client.createBucket(bucket_name)

        object_key = 's3client.py'
        file_path = os.path.join(os.getcwd(), object_key)
        client.createObject(bucket_name, object_key, file_path)

        temp_file_path = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))
        client.downloadObject(bucket_name, object_key, temp_file_path)

        self.assertEqual(client.computeMD5(file_path), client.computeMD5(temp_file_path))

        os.remove(temp_file_path)
        client.deleteObject(bucket_name, object_key)
        client.deleteBucket(bucket_name)

    def testShouldCreateExpectedPublicURL(self):
        client = S3Client(Credentials("0PN5J17HBGZHT7JJ3X82", "uV3F3YluFJax1cknvbcGwgjvx4QpvB+leU8dUj2o"))
        actual = client.publicURL('johnsmith', 'cute/puppy.jpg', datetime.datetime.fromtimestamp(1234))
        expected = "https://johnsmith.s3.amazonaws.com/cute/puppy.jpg" +\
                   "?AWSAccessKeyId=0PN5J17HBGZHT7JJ3X82" +\
                   "&Expires=1234" +\
                   "&Signature=HWHkXHVSQazVDcxkZaCkVlGz7vg%3D"
        self.assertEqual(expected, actual)

    def testCanDownloadFileUsingPublicURL(self):
        client = S3Client(loadcredentials(), True)

        bucket_name = "test-" + str(uuid.uuid4())
        client.createBucket(bucket_name)

        object_key = 's3client.py'
        file_path = os.path.join(os.getcwd(), object_key)
        client.createObject(bucket_name, object_key, file_path)

        temp_file_path = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))
        expires = datetime.datetime.now() + datetime.timedelta(days=1)
        urllib.urlretrieve(client.publicURL(bucket_name, object_key, expires), temp_file_path)

        self.assertEqual(client.computeMD5(file_path), client.computeMD5(temp_file_path))

        os.remove(temp_file_path)
        client.deleteObject(bucket_name, object_key)
        client.deleteBucket(bucket_name)

if __name__ == '__main__':
    unittest.main()
