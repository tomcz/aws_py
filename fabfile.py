from fabric.api import *
import aws, time, os, shutil

@task
def provision_activemq():
    """
    Setup an activemq connection broker
    """
    node = aws.provision_with_boto('broker')
    with connection_to_node(node):
        setup_puppet_standalone()
        apply_manifest("broker-activemq", node.hostname)

@task
def provision_node(node_name):
    """
    Create named node that talks to activemq
    """
    stomp_host = aws.get_node('broker').hostname
    node = aws.provision_with_boto(node_name)
    with connection_to_node(node):
        setup_puppet_standalone()
        apply_manifest("mcollective-node", stomp_host)

@task
def mco_ping():
    """
    Run mcollective ping on the broker
    """
    node = aws.provision_with_boto('broker')
    with connection_to_node(node):
        run('mco ping')

@task
def shell(node_name):
    """
    Create and/or connect to a named node
    """
    node = aws.provision_with_boto(node_name)
    wait_for_ssh_connection(node)

    filename = 'shell_' + node_name
    command = "ssh -i %s -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no %s@%s\n"
    command = command % (node.ssh_key_file, node.ssh_user, node.hostname)

    with open(filename, 'w') as script:
        script.write('#!/bin/sh\n')
        script.write(command)

    os.chmod(filename, 0755)
    print "Connect to [%s] instance using ./%s" % (node_name, filename)

@task
def terminate(node_name):
    """
    Terminate a named node
    """
    aws.terminate_instance(node_name)

@task
def destroy():
    """
    Terminate all nodes
    """
    aws.terminate_all_instances()

# --------------------------------------------------------------------
# Common provisioning functions
# --------------------------------------------------------------------

def connection_to_node(node):
    wait_for_ssh_connection(node)
    return settings(host_string=node.hostname, user=node.ssh_user, key_filename=node.ssh_key_file)

def wait_for_ssh_connection(node):
    if not os.path.isfile(node.ssh_key_file):
        key_file_path = prompt('SSH key file?')
        shutil.copyfile(os.path.expanduser(key_file_path), node.ssh_key_file)
        os.chmod(node.ssh_key_file, 0600)
    with settings(warn_only=True):
        result = check_ssh(node)
        while result.failed:
            print 'Waiting for SSH service ...'
            time.sleep(5)
            result = check_ssh(node)

def check_ssh(node):
    return local('nc -z -v -w 10 %s 22' % node.hostname)

def setup_puppet_standalone():
    with settings(warn_only=True):
        result = run('puppet --version')
    if result.failed:
        sudo('yum install -y puppet')
    with settings(warn_only=True):
        run("rm -f ec2-setup.tgz")
        run("rm -rf puppet/")
    local("tar czf /tmp/ec2-setup.tgz puppet/*")
    put("/tmp/ec2-setup.tgz", ".")
    run("tar xzf ec2-setup.tgz")

def apply_manifest(manifest, stomp_host):
    puppet_root = "/home/ec2-user/puppet"
    command = "FACTER_stomp_host=%s puppet apply --modulepath=%s/modules %s/manifests/%s.pp"
    sudo(command % (stomp_host, puppet_root, puppet_root, manifest))
