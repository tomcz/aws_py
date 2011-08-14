from properties import loadcredentials
from optparse import OptionParser
from s3client import S3Client
import os

parser = OptionParser(usage="usage: %prog [options]")
parser.add_option("-f", dest="file", help="File to upload", metavar="FILE")
parser.add_option("-b", dest="bucket", help="Destination bucket", metavar="BUCKET")

options, args = parser.parse_args()

if options.file and options.bucket:
    client = S3Client(loadcredentials())
    object_key = os.path.basename(options.file)
    print 'Sending', options.file, 'to', options.bucket, 'as', object_key
    client.createObject(options.bucket, object_key, options.file)
else:
    parser.print_help()
