import os, hashlib, hmac, base64

def loadcredentials():
    properties = {}
    prop_file = open(os.path.join(os.getenv('HOME'), '.s3dropbox'))
    for line in prop_file:
        text = line.strip()
        if len(text) > 0 and not text.startswith('#'):
            key, sep, val = text.partition('=')
            properties[key.strip()] = val.strip()
    prop_file.close()
    return Credentials(properties['AMAZON_ACCESS_KEY_ID'], properties['AMAZON_SECRET_ACCESS_KEY'])

class Credentials:
    def __init__(self, access_key_id, secret_access_key):
        self.secret_access_key = secret_access_key
        self.access_key_id = access_key_id

    def sign(self, text):
        digest = hmac.new(self.secret_access_key, text, hashlib.sha1).digest()
        return base64.b64encode(digest)
