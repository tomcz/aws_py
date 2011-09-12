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
plugin.stomp.host = ${activemq_host}
plugin.stomp.port = 6163
plugin.stomp.user = mcollective
plugin.stomp.password = marionette

# Facts
factsource = yaml
plugin.yaml = /etc/mcollective/facts.yaml
