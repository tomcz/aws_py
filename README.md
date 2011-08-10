Python bindings for Amazon Web Services
=======================================

This project comprises a useful set of python scripts written to help me administer AWS S3 buckets and CloudFront
distributions. This is by no means an exhaustive set of features, rather this is simply a compendium of what I
have found to be useful in dealing with AWS.

Requirements
------------

* These scripts have been written for Python 2.7.2 and may not work with other versions.
* S3 scripts require [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/).
* CloudFront scripts require the [Mako](http://www.makotemplates.org/) template library.
* All scripts look for a file called .s3dropbox in your home directory to provide the
  Amazon AWS authentication keys. This is a file in key=value format and follows the
  conventions set up by the [S3DropBox](https://github.com/tomcz/s3dropbox) project.

These scripts are covered by the [MIT License](http://www.opensource.org/licenses/mit-license.php).
