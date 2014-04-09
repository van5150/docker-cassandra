#!/usr/bin/env python

# Copyright (C) 2013 SignalFuse, Inc.

# Start script for Cassandra.
# Requires python-yaml for configuration reading/writing.

import os
import subprocess
import yaml

from maestro.guestutils import *
from maestro.extensions.logging.logstash import run_service

os.chdir(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..'))

CASSANDRA_CONFIG_FILE = os.path.join('conf', 'cassandra.yaml')
CASSANDRA_LOG4j_CONFIG = os.path.join('conf', 'log4j-server.properties')

# Read and parse the existing file.
with open(CASSANDRA_CONFIG_FILE) as f:
    conf = yaml.load(f)

# Update the configuration settings we care about.
conf.update({
    'cluster_name': os.environ.get('CLUSTER_NAME',
                                   '{}-cassandra'.format(get_environment_name())),
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

# Update the log4j config to disable file logging.
with open(CASSANDRA_LOG4j_CONFIG, 'w+') as f:
    f.write("""# Log4j configuration, logs to stdout
log4j.rootLogger=INFO,stdout
log4j.appender.stdout=org.apache.log4j.ConsoleAppender
log4j.appender.stdout.layout=org.apache.log4j.PatternLayout
log4j.appender.stdout.layout.ConversionPattern=%d{yyyy/MM/dd'T'HH:mm:ss.SSS} %-5p [%t] %c: %m%n
# Adding this to avoid thrift logging disconnect errors.
log4j.logger.org.apache.thrift.server.TNonblockingServer=ERROR
""")

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
run_service(['bin/cassandra', '-f'],
        logbase='/var/log/cassandra',
        logtarget='logstash')
