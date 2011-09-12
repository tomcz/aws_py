class activemq {
  group { "activemq":
    ensure => present,
    allowdupe => false
  }

  user { "activemq":
    ensure => present,
    allowdupe => false,
    gid => "activemq",
    require => Group["activemq"]
  }

  package { "java-1.6.0-openjdk":
    ensure => installed
  }

  package { "java-1.6.0-openjdk-devel":
    ensure => installed,
    require => Package["java-1.6.0-openjdk"]
  }

  package { "tanukiwrapper-3.2.3-1jpp":
    ensure => installed,
    provider => "rpm",
    source => "http://downloads.puppetlabs.com/mcollective/tanukiwrapper-3.2.3-1jpp.x86_64.rpm",
    require => [Package["java-1.6.0-openjdk-devel"], User["activemq"]]
  }

  package { "activemq-5.5.0-2.el5.noarch":
    ensure => installed,
    provider => "rpm",
    source => "http://downloads.puppetlabs.com/mcollective/activemq-5.5.0-2.el5.noarch.rpm",
    require => Package["tanukiwrapper-3.2.3-1jpp"]
  }

  package { "activemq-info-provider-5.5.0-2.el5.noarch":
    ensure => installed,
    provider => "rpm",
    source => "http://downloads.puppetlabs.com/mcollective/activemq-info-provider-5.5.0-2.el5.noarch.rpm",
    require => Package["activemq-5.5.0-2.el5.noarch"]
  }

  file { "/etc/activemq/activemq.xml":
    ensure => present,
    source => "/tmp/activemq.xml",
    mode => 0644,
    require => Package["activemq-info-provider-5.5.0-2.el5.noarch"],
    notify => Service["activemq"]
  }

  service { "activemq":
    ensure => running,
    require => [Package["activemq-info-provider-5.5.0-2.el5.noarch"], File["/etc/activemq/activemq.xml"]]
  }
}

class mcollective {
  include activemq
  
  package { "epel-release-5-4.noarch":
    ensure => installed,
    provider => "rpm",
    source => "http://download.fedoraproject.org/pub/epel/5/i386/epel-release-5-4.noarch.rpm"
  }

  package { "rubygem-stomp-1.1.8-1.el5.noarch":
    ensure => installed,
    require => Package["epel-release-5-4.noarch"]
  }

  package { "mcollective-common-1.2.1-1.el5.noarch":
    ensure => installed,
    provider => "rpm",
    source => "http://downloads.puppetlabs.com/mcollective/mcollective-common-1.2.1-1.el5.noarch.rpm",
    require => Package["rubygem-stomp-1.1.8-1.el5.noarch"]
  }

  package { "mcollective-client-1.2.1-1.el5.noarch":
    ensure => installed,
    provider => "rpm",
    source => "http://downloads.puppetlabs.com/mcollective/mcollective-client-1.2.1-1.el5.noarch.rpm",
    require => Package["mcollective-common-1.2.1-1.el5.noarch"]
  }

  package { "mcollective-1.2.1-1.el5.noarch":
    ensure => installed,
    provider => "rpm",
    source => "http://downloads.puppetlabs.com/mcollective/mcollective-1.2.1-1.el5.noarch.rpm",
    require => Package["mcollective-common-1.2.1-1.el5.noarch"]
  }

  file { "/etc/mcollective/client.cfg":
    ensure => present,
    source => "/tmp/client.cfg",
    mode => 0644,
    require => Package["mcollective-client-1.2.1-1.el5.noarch"]
  }

  file { "/etc/mcollective/server.cfg":
    ensure => present,
    source => "/tmp/server.cfg",
    mode => 0644,
    require => Package["mcollective-1.2.1-1.el5.noarch"],
    notify => Service["mcollective"]
  }

  service { "mcollective":
    ensure => running,
    require => [Package["mcollective-1.2.1-1.el5.noarch"], File["/etc/mcollective/server.cfg"], Service['activemq']]
  }
}

include mcollective
