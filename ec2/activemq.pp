class activemq {
  group { "activemq":
    ensure    => present,
    allowdupe => false
  }

  user { "activemq":
    ensure    => present,
    allowdupe => false,
    gid       => "activemq",
    require   => Group["activemq"]
  }

  package { "java-1.6.0-openjdk":
    ensure => installed
  }

  package { "java-1.6.0-openjdk-devel":
    ensure  => installed,
    require => Package["java-1.6.0-openjdk"]
  }

  package { "tanukiwrapper-3.5.9-1.el6.i686":
    ensure   => installed,
    provider => "rpm",
    source   => "http://downloads.puppetlabs.com/mcollective/tanukiwrapper-3.5.9-1.el6.i686.rpm",
    require  => [Package["java-1.6.0-openjdk-devel"], User["activemq"]]
  }

  package { "activemq-5.5.0-1.el6":
    ensure   => installed,
    provider => "rpm",
    source   => "http://downloads.puppetlabs.com/mcollective/activemq-5.5.0-1.el6.noarch.rpm",
    require  => Package["tanukiwrapper-3.5.9-1.el6.i686"]
  }

  package { "activemq-info-provider-5.5.0-1.el6":
    ensure   => installed,
    provider => "rpm",
    source   => "http://downloads.puppetlabs.com/mcollective/activemq-info-provider-5.5.0-1.el6.noarch.rpm",
    require  => Package["activemq-5.5.0-1.el6"]
  }

  file { "/etc/activemq/activemq.xml":
    ensure  => present,
    source  => "/tmp/activemq.xml",
    mode    => 0644,
    group   => "activemq",
    owner   => "activemq",
    require => Package["activemq-info-provider-5.5.0-1.el6"],
    notify  => Service["activemq"]
  }

  service { "activemq":
    ensure  => running,
    enable  => true,
    require => [Package["activemq-info-provider-5.5.0-1.el6"], File["/etc/activemq/activemq.xml"]]
  }
}

class mcollective {
  include activemq

  yumrepo { "epel":
    enabled => 1
  }

  package { "rubygems":
    ensure => installed
  }

  package { "rubygem-stomp":
    ensure  => installed,
    require => [Package["rubygems"], Yumrepo["epel"]]
  }

  package { "mcollective-common-1.3.1-2.el6":
    ensure   => installed,
    provider => "rpm",
    source   => "http://downloads.puppetlabs.com/mcollective/mcollective-common-1.3.1-2.el6.noarch.rpm",
    require  => Package["rubygem-stomp"]
  }

  package { "mcollective-client-1.3.1-2.el6":
    ensure   => installed,
    provider => "rpm",
    source   => "http://downloads.puppetlabs.com/mcollective/mcollective-client-1.3.1-2.el6.noarch.rpm",
    require  => Package["mcollective-common-1.3.1-2.el6"]
  }

  package { "mcollective-1.3.1-2.el6":
    ensure   => installed,
    provider => "rpm",
    source   => "http://downloads.puppetlabs.com/mcollective/mcollective-1.3.1-2.el6.noarch.rpm",
    require  => Package["mcollective-common-1.3.1-2.el6"]
  }

  file { "/etc/mcollective/client.cfg":
    ensure  => present,
    source  => "/tmp/client.cfg",
    mode    => 0644,
    group   => "root",
    owner   => "root",
    require => Package["mcollective-client-1.3.1-2.el6"]
  }

  file { "/etc/mcollective/server.cfg":
    ensure  => present,
    source  => "/tmp/server.cfg",
    mode    => 0644,
    group   => "root",
    owner   => "root",
    require => Package["mcollective-1.3.1-2.el6"],
    notify  => Service["mcollective"]
  }

  service { "mcollective":
    ensure  => running,
    enable  => true,
    require => [Package["mcollective-1.3.1-2.el6"], File["/etc/mcollective/server.cfg"], Service['activemq']]
  }
}

include mcollective
