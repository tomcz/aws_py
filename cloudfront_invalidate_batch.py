from cloudfront import CommonParameters, send_request
from mako.template import Template
from optparse import OptionParser
import uuid

class Parameters(CommonParameters):
    def __init__(self, distribution_id, headers):
        CommonParameters.__init__(self, 'POST', headers)
        self.distribution_id = distribution_id

    def createPath(self):
        return '/2010-11-01/distribution/%s/invalidation' % self.distribution_id

if __name__ == '__main__':
    parser = OptionParser(usage="usage: %prog [options] objectkey1 objectkey2 ...")
    parser.add_option("-d", dest="distribution_id", help="Distribution ID", metavar="ID")

    options, args = parser.parse_args()

    if options.distribution_id and len(args) > 0:
        callerRef = str(uuid.uuid4())

        template = Template(filename='cloudfront_invalidate_batch.xml')
        invalidate_request = template.render(objects=args, callerRef=callerRef)

        headers = {'Content-Type': 'text/xml', 'Content-Length': str(len(invalidate_request))}
        parameters = Parameters(options.distribution_id, headers)

        send_request(parameters, invalidate_request)
    else:
        parser.print_help()
