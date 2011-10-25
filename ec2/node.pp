class mcollective {

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

  package { "mcollective-1.3.1-2.el6":
    ensure   => installed,
    provider => "rpm",
    source   => "http://downloads.puppetlabs.com/mcollective/mcollective-1.3.1-2.el6.noarch.rpm",
    require  => Package["mcollective-common-1.3.1-2.el6"]
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
    require => [Package["mcollective-1.3.1-2.el6"], File["/etc/mcollective/server.cfg"]]
  }
}

include mcollective
