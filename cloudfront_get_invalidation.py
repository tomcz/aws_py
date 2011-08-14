from cloudfront import CommonParameters, send_request
from optparse import OptionParser

class Parameters(CommonParameters):
    def __init__(self, distribution_id, invalidation_id):
        CommonParameters.__init__(self, 'GET')
        self.distribution_id = distribution_id
        self.invalidation_id = invalidation_id

    def createPath(self):
        return '/2010-11-01/distribution/%s/invalidation/%s' % (self.distribution_id, self.invalidation_id)

if __name__ == '__main__':
    parser = OptionParser(usage="usage: %prog [options]")
    parser.add_option("-d", dest="distribution_id", help="Distribution ID", metavar="ID")
    parser.add_option("-i", dest="invalidation_id", help="Invalidation ID", metavar="ID")

    options, args = parser.parse_args()

    if options.distribution_id and options.invalidation_id:
        send_request(Parameters(options.distribution_id, options.invalidation_id))
    else:
        parser.print_help()
