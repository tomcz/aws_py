class mcollective::server {
  include mcollective::common

  package { "mcollective-1.3.1-2.el6":
    ensure   => installed,
    provider => "rpm",
    source   => "http://archives.watchitlater.com/rpms/mcollective-1.3.1-2.el6.noarch.rpm",
    require  => Package["mcollective-common-1.3.1-2.el6"],
  }

  file { "/etc/mcollective/server.cfg":
    ensure  => present,
    content => template("mcollective/server.cfg.erb"),
    mode    => 0644,
    group   => "root",
    owner   => "root",
    require => Package["mcollective-1.3.1-2.el6"],
    notify  => Service["mcollective"],
  }

  service { "mcollective":
    ensure  => running,
    enable  => true,
    require => [Package["mcollective-1.3.1-2.el6"], File["/etc/mcollective/server.cfg"]],
  }
}
