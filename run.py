#!/usr/bin/env python

# Start script for Cassandra.

import os
import re
import sys
import yaml

os.chdir(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..'))

CASSANDRA_CONFIG_FILE = 'conf/cassandra.yaml'

CONTAINER_NAME = os.environ.get('CONTAINER_NAME', '')
assert CONTAINER_NAME, 'Container name is missing!'
CASSANDRA_CONFIG_BASE = re.sub(r'[^\w]', '_', CONTAINER_NAME).upper()

CONTAINER_HOST_ADDRESS = os.environ.get('CONTAINER_HOST_ADDRESS', '')
assert CONTAINER_HOST_ADDRESS, 'Container host address is required for Gossip discovery!'

CASSANDRA_CONFIG_CLUSTER_NAME = os.environ.get('CASSANDRA_CONFIG_CLUSTER_NAME', 'local-cassandra')
CASSANDRA_CONFIG_STORAGE_PORT = int(os.environ.get('CASSANDRA_%s_STORAGE_PORT' % CASSANDRA_CONFIG_BASE, 7000))
CASSANDRA_CONFIG_TRANSPORT_PORT = int(os.environ.get('CASSANDRA_%s_TRANSPORT_PORT' % CASSANDRA_CONFIG_BASE, 9042))
CASSANDRA_CONFIG_RPC_PORT = int(os.environ.get('CASSANDRA_%s_RPC_PORT' % CASSANDRA_CONFIG_BASE, 9160))
CASSANDRA_CONFIG_SEED_PEERS = ','.join(
    map(lambda x: os.environ[x],
        filter(lambda x: x.startswith('CASSANDRA_') and x.endswith('_HOST'),
               os.environ.keys()))) \
    or '127.0.0.1'

# Read and parse the existing file.
with open(CASSANDRA_CONFIG_FILE) as f:
    conf = yaml.load(f)

# Update the configuration settings we care about.
conf.update({
    'cluster_name': CASSANDRA_CONFIG_CLUSTER_NAME,
    'data_file_directories': ['/var/lib/cassandra/data'],
    'commitlog_directory': '/var/lib/cassandra/commitlog',
    'listen_address': '0.0.0.0',
    'broadcast_address': CONTAINER_HOST_ADDRESS,
    'rpc_address': '0.0.0.0',
    'storage_port': CASSANDRA_CONFIG_STORAGE_PORT,
    'native_transport_port': CASSANDRA_CONFIG_TRANSPORT_PORT,
    'rpc_port': CASSANDRA_CONFIG_RPC_PORT,
})

conf['seed_provider'][0]['parameters'][0]['seeds'] = CASSANDRA_CONFIG_SEED_PEERS

# Output the updated configuration.
with open(CASSANDRA_CONFIG_FILE, 'w+') as f:
    yaml.dump(conf, f, default_flow_style=False)

# Start Cassandra in the foreground.
os.execl('bin/cassandra', 'cassandra', '-f')
