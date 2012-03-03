import os, hashlib, hmac, base64
from ConfigParser import SafeConfigParser
from fabric.operations import prompt

def loadcredentials():
    config = SafeConfigParser()
    config_file_path = os.path.join(os.path.dirname(__file__), 'venv', 'aws.ini')

    if not os.path.isfile(config_file_path):
        config.add_section('aws')
        config.set('aws', 'access_key_id', prompt("AWS access key id?"))
        config.set('aws', 'secret_access_key', prompt("AWS secret access key?"))
        with open(config_file_path, 'w') as fp:
            config.write(fp)
    else:
        with open(config_file_path) as fp:
            config.readfp(fp)

    access_key = config.get('aws', 'access_key_id')
    secret_key = config.get('aws', 'secret_access_key')
    return Credentials(access_key, secret_key)

class Credentials:
    def __init__(self, access_key_id, secret_access_key):
        self.secret_access_key = secret_access_key
        self.access_key_id = access_key_id

    def sign(self, text):
        digest = hmac.new(self.secret_access_key, text, hashlib.sha1).digest()
        return base64.b64encode(digest)
