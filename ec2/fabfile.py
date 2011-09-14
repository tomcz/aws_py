# pip install boto
# pip install fabric
# pip install mako

from mako.template import Template
from fabric.api import *
import aws, time

@task
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

@task
def provision_node(node_name):
    node = aws.provision_with_boto(node_name)
    configure_server_cfg(aws.read_config().get('activemq', 'public_dns_name'))
    with connection_to_node(node):
        setup_puppet_standalone()
        put('/tmp/server.cfg', '/tmp')
        put('node.pp', '/tmp')
        sudo('puppet apply /tmp/node.pp')

@task
def shell(node_name):
    node = aws.provision_with_boto(node_name)
    with connection_to_node(node):
        open_shell()

@task
def mco_ping():
    node = aws.provision_with_boto('activemq')
    with connection_to_node(node):
        run('mco ping')

@task
def cleanup(node_name = None):
    config = aws.read_config()
    if node_name:
        if config.has_section(node_name):
            aws.terminate_instance(node_name)
    else:
        for section in config.sections():
            aws.terminate_instance(section)

@task
def destroy():
    aws.terminate_all_instances()

# --------------------------------------------------------------------
# Common provisioning functions
# --------------------------------------------------------------------

def configure_server_cfg(activemq_host):
    template = Template(filename='server.cfg.mako')
    content = template.render(activemq_host=activemq_host)
    with open('/tmp/server.cfg', 'w') as fp:
        fp.write(content)

def connection_to_node(node):
    wait_for_ssh_connection(node)
    return settings(host_string=node.hostname, user=node.ssh_user, key_filename=node.ssh_key_file)

def wait_for_ssh_connection(node):
    with settings(warn_only=True):
        result = check_ssh(node)
        while result.failed:
            print 'Waiting for SSH service ...'
            time.sleep(10)
            result = check_ssh(node)

def check_ssh(node):
    return local('nc -zv %s 22' % node.hostname)

def setup_puppet_standalone():
    with settings(warn_only=True):
        result = run('puppet --version')
    if result.failed:
        sudo('yum install -y puppet')
