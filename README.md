Python bindings for Amazon Web Services
=======================================

This project comprises a useful set of python scripts written to help me administer AWS S3 buckets, CloudFront
distributions and EC2 instances. This is by no means an exhaustive set of features, rather this is simply a
compendium of what I have found to be useful in dealing with AWS.

Usage
-----

    $> ./run
    Available commands:

        destroy             Terminate all nodes
        mco_ping            Run mcollective ping on the broker
        provision_activemq  Setup an activemq connection broker
        provision_node      Create named node that talks to activemq
        shell               Create and/or connect to a named node
        terminate           Terminate a named node

    OR ./run <any local python script>

Requirements
------------

You should not need to do anything special except to invoke the `./run` script.
It should do the rest including setting up the required python libraries in a virtualenv environment.

Notes
-----

* These scripts have been written for Python 2.7.2 and may not work with other versions.
* S3 scripts require [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/).
* CloudFront scripts require the [Mako](http://www.makotemplates.org/) template library.
* EC2 scripts additionally require both [boto](http://boto.cloudhackers.com/index.html)
  and [fabric](http://docs.fabfile.org/en/1.4.0/index.html) in order to provision and control
  multiple EC2 instances.

License
-------

These scripts are covered by the [MIT License](http://www.opensource.org/licenses/mit-license.php).
