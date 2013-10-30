#!/usr/bin/env python

# Start script for Cassandra.

import os
import sys
import yaml

os.chdir(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..'))

CASSANDRA_CONFIG_FILE = 'conf/cassandra.yaml'

# Environment variables driving the Cassandra configuration and their defaults.
CASSANDRA_CONFIG_CLUSTER_NAME = os.environ.get('CASSANDRA_CONFIG_CLUSTER_NAME', 'Cassandra cluster')
CASSANDRA_CONFIG_DATA_DIRS = os.environ.get('CASSANDRA_CONFIG_DATA_DIRS', '/var/lib/cassandra/data')
CASSANDRA_CONFIG_COMMITLOG_DIR = os.environ.get('CASSANDRA_CONFIG_COMMITLOG_DIR', '/var/lib/cassandra/commitlog')
CASSANDRA_CONFIG_STORAGE_PORT = int(os.environ.get('CASSANDRA_CONFIG_STORAGE_PORT', 7000))
CASSANDRA_CONFIG_TRANSPORT_PORT = int(os.environ.get('CASSANDRA_CONFIG_TRANSPORT_PORT', 9042))
CASSANDRA_CONFIG_RPC_PORT = int(os.environ.get('CASSANDRA_CONFIG_RPC_PORT', 9160))
CASSANDRA_CONFIG_BROADCAST_ADDRESS = os.environ.get('CASSANDRA_CONFIG_BROADCAST_ADDRESS', '127.0.0.1')
CASSANDRA_CONFIG_SEED_PEERS = os.environ.get('CASSANDRA_CONFIG_SEED_PEERS', '127.0.0.1')

# Read and parse the existing file.
with open(CASSANDRA_CONFIG_FILE) as f:
    conf = yaml.load(f)

# Update the configuration settings we care about.
conf.update({
    'cluster_name': CASSANDRA_CONFIG_CLUSTER_NAME,
    'data_file_directories': CASSANDRA_CONFIG_DATA_DIRS.split(','),
    'commitlog_directory': CASSANDRA_CONFIG_COMMITLOG_DIR,
    'listen_address': '0.0.0.0',
    'broadcast_address': CASSANDRA_CONFIG_BROADCAST_ADDRESS,
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
