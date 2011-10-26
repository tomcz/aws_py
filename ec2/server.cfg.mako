topicprefix = /topic/
main_collective = mcollective
collectives = mcollective
libdir = /usr/libexec/mcollective
logfile = /var/log/mcollective.log
loglevel = info
daemonize = 1

# Plugins
securityprovider = psk
plugin.psk = 2!rmZk>9#A

connector = stomp
plugin.stomp.pool.size = 1
plugin.stomp.pool.host1 = ${activemq_host}
plugin.stomp.pool.port1 = 6163
plugin.stomp.pool.user1 = mcollective
plugin.stomp.pool.password1 = marionette
plugin.stomp.pool.ssl1 = true

# Facts
factsource = yaml
plugin.yaml = /etc/mcollective/facts.yaml
