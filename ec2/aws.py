from boto.ec2 import connect_to_region
from ConfigParser import SafeConfigParser
import os, time

USERNAME = 'ec2-user'
AMI_ID = 'ami-c7c99982'
INSTANCE_TYPE = 't1.micro'

EC2_REGION = 'us-west-1'
EC2_SSH_KEY_NAME = 'us-west'
EC2_SSH_KEY_PATH = os.path.join(os.getenv('HOME'), '.aws', 'us-west.pem')

INSTANCES_FILE = os.path.join(os.getenv('HOME'), '.aws', 'aws_instances.ini')
S3_DROP_BOX_FILE = os.path.join(os.getenv('HOME'), '.s3dropbox')

class Node:
    def __init__(self, public_dns_name):
        self.hostname = public_dns_name
        self.ssh_key_file = EC2_SSH_KEY_PATH
        self.ssh_user = USERNAME

def provision_with_boto(name):
    config = read_config()
    if config.has_section(name):
        return Node(config.get(name, 'public_dns_name'))
    else:
        return Node(run_instance(name))

def connect():
    properties = {}
    with open(S3_DROP_BOX_FILE) as prop_file:
        for line in prop_file:
            text = line.strip()
            if len(text) > 0 and not text.startswith('#'):
                key, sep, val = text.partition('=')
                properties[key.strip()] = val.strip()
    access_key = properties['AMAZON_ACCESS_KEY_ID']
    secret_key = properties['AMAZON_SECRET_ACCESS_KEY']
    return connect_to_region(EC2_REGION, aws_access_key_id=access_key, aws_secret_access_key=secret_key)

def run_instance(name):
    conn = connect()
    res = conn.run_instances(AMI_ID, key_name=EC2_SSH_KEY_NAME, instance_type=INSTANCE_TYPE)
    instance = res.instances[0]

    print "Waiting for", name, "to start ..."
    time.sleep(10)
    instance.update()

    while instance.state != 'running':
        time.sleep(10)
        instance.update()

    conn.create_tags([instance.id], {'Name': name})

    config = read_config()
    config.add_section(name)
    config.set(name, 'instance_id', instance.id)
    config.set(name, 'public_dns_name', instance.public_dns_name)
    write_config(config)

    return instance.public_dns_name

def terminate_instance(name):
    config = read_config()
    instance_id = config.get(name, 'instance_id')

    conn = connect()
    conn.terminate_instances([instance_id])

    config.remove_section(name)
    write_config(config)

def write_config(config):
    with open(INSTANCES_FILE, 'w') as fp:
        config.write(fp)

def read_config():
    config = SafeConfigParser()
    if os.path.isfile(INSTANCES_FILE):
        with open(INSTANCES_FILE) as fp:
            config.readfp(fp)
    return config
