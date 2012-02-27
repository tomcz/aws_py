class mcollective::client {
  include mcollective::common

  package { "mcollective-client-1.3.1-2.el6":
    ensure   => installed,
    provider => "rpm",
    source   => "http://watchitlater.com/rpms/mcollective-client-1.3.1-2.el6.noarch.rpm",
    require  => Package["mcollective-common-1.3.1-2.el6"]
  }

  file { "/etc/mcollective/client.cfg":
    ensure  => present,
    content => template("mcollective/client.cfg.erb"),
    mode    => 0644,
    group   => "root",
    owner   => "root",
    require => Package["mcollective-client-1.3.1-2.el6"]
  }
}
