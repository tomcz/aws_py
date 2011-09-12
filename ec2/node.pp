class mcollective {
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

  package { "mcollective-1.2.1-1.el5.noarch":
    ensure => installed,
    provider => "rpm",
    source => "http://downloads.puppetlabs.com/mcollective/mcollective-1.2.1-1.el5.noarch.rpm",
    require => Package["mcollective-common-1.2.1-1.el5.noarch"]
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
    enable => true,
    require => [Package["mcollective-1.2.1-1.el5.noarch"], File["/etc/mcollective/server.cfg"]]
  }
}

include mcollective
