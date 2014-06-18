#!/usr/bin/env python

# Copyright (C) 2013 SignalFuse, Inc.

# Start script for Cassandra.
# Requires python-yaml for configuration reading/writing.

import os
import subprocess
import yaml

from maestro.guestutils import *

os.chdir(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..'))

CASSANDRA_CONFIG_FILE = os.path.join('conf', 'cassandra.yaml')
CASSANDRA_LOGGING_CONFIG = os.path.join('conf', 'log4j-server.properties')

LOG_PATTERN = "%d{yyyy'-'MM'-'dd'T'HH:mm:ss.SSSXXX} %-5p [%-35.35t] [%-36.36c]: %m%n"

# Read and parse the existing file.
with open(CASSANDRA_CONFIG_FILE) as f:
    conf = yaml.load(f)

# Update the configuration settings we care about.
conf.update({
    'cluster_name': os.environ.get('CLUSTER_NAME',
                                   '{}-{}'.format(get_environment_name(), get_service_name())),
    'data_file_directories': ['/var/lib/cassandra/data'],
    'commitlog_directory': '/var/lib/cassandra/commitlog',
    'listen_address': get_container_internal_address(),
    'broadcast_address': get_container_host_address(),
    'rpc_address': get_container_internal_address(),
    'storage_port': get_port('storage', 7000),
    'native_transport_port': get_port('transport', 9042),
    'rpc_port': get_port('rpc', 9160),
})

conf['seed_provider'][0]['parameters'][0]['seeds'] = \
    ','.join(get_node_list(get_service_name(), minimum=0)) or '127.0.0.1'

# Output the updated configuration.
with open(CASSANDRA_CONFIG_FILE, 'w+') as f:
    yaml.dump(conf, f, default_flow_style=False)

# Setup the logging configuration.
with open(CASSANDRA_LOGGING_CONFIG, 'w+') as f:
    f.write("""# Log4j configuration, logs to rotating file
log4j.rootLogger=INFO,R

log4j.appender.R=org.apache.log4j.RollingFileAppender
log4j.appender.R.File=/var/log/%s/%s.log
log4j.appender.R.MaxFileSize=100MB
log4j.appender.R.MaxBackupIndex=10
log4j.appender.R.layout=org.apache.log4j.PatternLayout
log4j.appender.R.layout.ConversionPattern=%s
""" % (get_service_name(), get_container_name(), LOG_PATTERN))

# Setup the JMX Java agent and other JVM options.
os.environ['JVM_OPTS'] = ' '.join([
    '-server',
    '-showversion',
    '-javaagent:lib/jmxagent.jar',
    '-Dsf.jmxagent.port={}'.format(get_port('jmx', -1)),
    '-Djava.rmi.server.hostname={}'.format(get_container_host_address()),
    '-Dvisualvm.display.name="{}/{}"'.format(get_environment_name(), get_container_name()),
    os.environ.get('JVM_OPTS', ''),
])

# Throw the default JMX on another port we don't care about.
subprocess.check_call(['sed', '-ie',
    's/^JMX_PORT="7199"$/JMX_PORT="17199"/',
    'conf/cassandra-env.sh'])

# Start Cassandra in the foreground.
os.execl('bin/cassandra', 'cassandra', '-f')
