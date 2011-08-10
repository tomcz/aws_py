from cloudfront import CommonParameters, send_request
from optparse import OptionParser

class Parameters(CommonParameters):
    def __init__(self, distribution_id):
        CommonParameters.__init__(self, 'GET')
        self.distribution_id = distribution_id

    def createPath(self):
        return '/2010-11-01/distribution/%s/invalidation' % self.distribution_id

if __name__ == '__main__':
    parser = OptionParser(usage="usage: %prog [options]")
    parser.add_option("-d", dest="distribution_id", help="Distribution ID", metavar="ID")

    (options, args) = parser.parse_args()

    if options.distribution_id:
        send_request(Parameters(options.distribution_id))
    else:
        parser.print_help()
