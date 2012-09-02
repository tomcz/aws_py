class mcollective::common {

  yumrepo { "epel":
    enabled => 1,
  }

  package { "rubygems":
    ensure => installed,
  }

  package { "rubygem-stomp":
    ensure  => installed,
    require => [Package["rubygems"], Yumrepo["epel"]],
  }

  package { "mcollective-common-1.3.1-2.el6":
    ensure   => installed,
    provider => "rpm",
    source   => "http://archives.watchitlater.com/rpms/mcollective-common-1.3.1-2.el6.noarch.rpm",
    require  => Package["rubygem-stomp"],
  }
}
