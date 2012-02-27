class activemq {

  group { "activemq":
    ensure    => present,
    allowdupe => false,
  }

  user { "activemq":
    ensure    => present,
    allowdupe => false,
    gid       => "activemq",
    require   => Group["activemq"],
  }

  package { "java-1.6.0-openjdk":
    ensure => installed,
  }

  package { "java-1.6.0-openjdk-devel":
    ensure  => installed,
    require => Package["java-1.6.0-openjdk"],
  }

  package { "tanukiwrapper-3.5.9-1.el6.i686":
    ensure   => installed,
    provider => "rpm",
    source   => "http://watchitlater.com/rpms/tanukiwrapper-3.5.9-1.el6.i686.rpm",
    require  => [Package["java-1.6.0-openjdk-devel"], User["activemq"]],
  }

  package { "activemq-5.5.0-1.el6":
    ensure   => installed,
    provider => "rpm",
    source   => "http://watchitlater.com/rpms/activemq-5.5.0-1.el6.noarch.rpm",
    require  => Package["tanukiwrapper-3.5.9-1.el6.i686"],
  }

  package { "activemq-info-provider-5.5.0-1.el6":
    ensure   => installed,
    provider => "rpm",
    source   => "http://watchitlater.com/rpms/activemq-info-provider-5.5.0-1.el6.noarch.rpm",
    require  => Package["activemq-5.5.0-1.el6"],
  }

  file { "/etc/activemq/activemq.xml":
    ensure  => present,
    source  => "puppet:///modules/activemq/activemq.xml",
    mode    => 0644,
    group   => "activemq",
    owner   => "activemq",
    require => Package["activemq-info-provider-5.5.0-1.el6"],
    notify  => Service["activemq"],
  }

  file { "/etc/activemq/broker.ks":
    ensure  => present,
    source  => "puppet:///modules/activemq/broker.ks",
    mode    => 0644,
    group   => "activemq",
    owner   => "activemq",
    require => Package["activemq-info-provider-5.5.0-1.el6"],
    notify  => Service["activemq"],
  }

  service { "activemq":
    ensure  => running,
    enable  => true,
    require => [Package["activemq-info-provider-5.5.0-1.el6"],
                File["/etc/activemq/activemq.xml"],
                File["/etc/activemq/broker.ks"]],
  }
}
