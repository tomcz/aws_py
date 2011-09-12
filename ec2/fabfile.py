# pip install boto
# pip install fabric
# pip install mako

from mako.template import Template
from fabric.api import *
import aws

def provision_activemq():
    node = aws.provision_with_boto('activemq')
    configure_server_cfg(node.hostname)
    with connection_to_node(node):
        setup_puppet_standalone()
        put('/tmp/server.cfg', '/tmp')
        put('client.cfg', '/tmp')
        put('activemq.xml', '/tmp')
        put('activemq.pp', '/tmp')
        sudo('puppet apply /tmp/activemq.pp')

def provision_node(node_name):
    node = aws.provision_with_boto(node_name)
    configure_server_cfg(aws.read_config().get('activemq', 'public_dns_name'))
    with connection_to_node(node):
        setup_puppet_standalone()
        put('/tmp/server.cfg', '/tmp')
        put('node.pp', '/tmp')
        sudo('puppet apply /tmp/node.pp')

def mco_ping():
    node = aws.provision_with_boto('activemq')
    with connection_to_node(node):
        run('mco ping')

def cleanup():
    config = aws.read_config()
    for section in config.sections():
        aws.terminate_instance(section)

# --------------------------------------------------------------------
# Common provisioning functions
# --------------------------------------------------------------------

def configure_server_cfg(activemq_host):
    template = Template(filename='server.cfg.mako')
    content = template.render(activemq_host=activemq_host)
    with open('/tmp/server.cfg', 'w') as fp:
        fp.write(content)

def connection_to_node(node):
    return settings(host_string=node.hostname, user=node.ssh_user, key_filename=node.ssh_key_file)

def setup_puppet_standalone():
    with settings(warn_only=True):
        result = run("puppet --version")
    if result.failed:
        sudo('yum install -y puppet')
