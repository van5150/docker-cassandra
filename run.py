#!/usr/bin/env python

# Copyright (C) 2013 SignalFuse, Inc.

# Start script for Cassandra.
# Requires python-yaml for configuration reading/writing.

import os
import re
import sys
import yaml

from maestro.guestutils import *

os.chdir(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..'))

CASSANDRA_CONFIG_FILE = 'conf/cassandra.yaml'

# Read and parse the existing file.
with open(CASSANDRA_CONFIG_FILE) as f:
    conf = yaml.load(f)

# Update the configuration settings we care about.
conf.update({
    'cluster_name': os.environ.get('CLUSTER_NAME', 'local-cassandra'),
    'data_file_directories': ['/var/lib/cassandra/data'],
    'commitlog_directory': '/var/lib/cassandra/commitlog',
    'listen_address': '0.0.0.0',
    'broadcast_address': get_container_host_address(),
    'rpc_address': '0.0.0.0',
    'storage_port': get_port('storage', 7000),
    'native_transport_port': get_port('transport', 9042),
    'rpc_port': get_port('rpc', 9160),
})

conf['seed_provider'][0]['parameters'][0]['seeds'] = \
    ','.join(get_node_list(get_service_name(), minimum=0)) or '127.0.0.1'

# Output the updated configuration.
with open(CASSANDRA_CONFIG_FILE, 'w+') as f:
    yaml.dump(conf, f, default_flow_style=False)

# Start Cassandra in the foreground.
os.execl('bin/cassandra', 'cassandra', '-f')
