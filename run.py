#!/usr/bin/env python

# Copyright (C) 2013 SignalFuse, Inc.

# Start script for Cassandra.
# Requires python-yaml for configuration reading/writing.

import json
import logging
import os
import signal
import subprocess
import sys
import time
import uuid
import yaml

from kazoo.client import KazooClient

from maestro.guestutils import get_container_host_address, \
    get_container_name, \
    get_container_internal_address, \
    get_environment_name, \
    get_node_list, \
    get_port, \
    get_service_name

# Setup logging for Kazoo.
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

os.chdir(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..'))

CASSANDRA_CONFIG_FILE = os.path.join('conf', 'cassandra.yaml')
CASSANDRA_LOGGING_CONFIG = os.path.join('conf', 'log4j-server.properties')
CASSANDRA_CLUSTER_NAME = os.environ.get('CLUSTER_NAME',
                                        '{}-{}'.format(get_environment_name(), get_service_name()))

CASSANDRA_ZOOKEEPER_BASE = os.environ.get('ZOOKEEPER_BASE',
                                          '/{}/{}'.format(get_environment_name(), CASSANDRA_CLUSTER_NAME))

CQL_PORT = get_port('transport', 9042)
THRIFT_PORT = get_port('rpc', 9160)

LOG_PATTERN = "%d{yyyy'-'MM'-'dd'T'HH:mm:ss.SSSXXX} %-5p [%-35.35t] [%-36.36c]: %m%n"

LOG_CONFIG = """# Log4j configuration, logs to rotating file
log4j.rootLogger=INFO,R

log4j.appender.R=org.apache.log4j.RollingFileAppender
log4j.appender.R.File=/var/log/%s/%s.log
log4j.appender.R.MaxFileSize=100MB
log4j.appender.R.MaxBackupIndex=10
log4j.appender.R.layout=org.apache.log4j.PatternLayout
log4j.appender.R.layout.ConversionPattern=%s
"""


def advertise_zk(service, retries=3):
    zk_nodes = ','.join(get_node_list('zookeeper', ports=['client'], minimum=0))
    if "NON_SEED_NODE" in os.environ:
        # this node is explicitly marked as non-seed: don't advertise
        return None
    elif not zk_nodes:
        # No zookeeper nodes registered: don't advertise
        return None
    # implied else: advertize this node in zookeeper

    inst_id = str(uuid.uuid1())

    # TODO this (partially) mimics the way Curator-Discovery formats its
    # advertisements. We'll probably pull this into a helper library at some
    # point. See http://curator.apache.org/curator-x-discovery/ for details.
    inst = {
        "name": CASSANDRA_CLUSTER_NAME,
        "id": inst_id,
        "address": get_container_host_address(),
        "port": CQL_PORT,
        "registrationTimeUTC": long(time.time() * 1000),
        "serviceType": "DYNAMIC",
        "payload": {
            "cqlPort": CQL_PORT,
            "thriftPort": THRIFT_PORT,
        }
    }
    znode = CASSANDRA_ZOOKEEPER_BASE + '/' + inst_id
    while retries >= 0:
        # Connect to the ZooKeeper nodes. Use a pretty large timeout in case they were
        # just started. We should wait for them for a little while.
        zk = KazooClient(hosts=zk_nodes, timeout=30000)
        try:
            zk.start()
            zk.create(znode, json.dumps(inst), ephemeral=True, makepath=True)
            return zk
        except:
            retries -= 1
    else:
        sys.stderr.write("Could not advertise in ZooKeeper!")
        service.terminate()
        sys.exit(1)


def generate_configs():
    # Read and parse the existing file.
    with open(CASSANDRA_CONFIG_FILE) as f:
        conf = yaml.load(f)

    # Update the configuration settings we care about.
    conf.update({
        'cluster_name': CASSANDRA_CLUSTER_NAME,
        'data_file_directories': ['/var/lib/cassandra/data'],
        'commitlog_directory': '/var/lib/cassandra/commitlog',
        'listen_address': get_container_internal_address(),
        'broadcast_address': get_container_host_address(),
        'rpc_address': get_container_internal_address(),
        'storage_port': get_port('storage', 7000),
        'native_transport_port': CQL_PORT,
        'rpc_port': THRIFT_PORT,
    })

    conf['seed_provider'][0]['parameters'][0]['seeds'] = \
        ','.join(get_node_list(get_service_name(), minimum=0)) or '127.0.0.1'

    # Output the updated configuration.
    with open(CASSANDRA_CONFIG_FILE, 'w+') as f:
        yaml.dump(conf, f, default_flow_style=False)

    # Setup the logging configuration.
    with open(CASSANDRA_LOGGING_CONFIG, 'w+') as f:
        f.write(LOG_CONFIG % (get_service_name(), get_container_name(), LOG_PATTERN))


def start_cassandra():
    # Setup the JMX Java agent and other JVM options.
    jvm_opts = [
        '-server',
        '-showversion',
        '-Dvisualvm.display.name="{}/{}"'.format(
            get_environment_name(), get_container_name()),
    ]

    jmx_port = get_port('jmx', -1)
    if jmx_port != -1:
        jvm_opts += [
            '-Dcom.sun.management.jmxremote.rmi.port={}'.format(jmx_port),
            '-Djava.rmi.server.hostname={}'.format(get_container_host_address()),
            '-Dcom.sun.management.jmxremote.local.only=false',
        ]
        subprocess.check_call(['sed', '-ie',
                              's/^JMX_PORT="7199"$/JMX_PORT="{}"/'.format(jmx_port),
                              'conf/cassandra-env.sh'])

    os.environ['JVM_OPTS'] = ' '.join(jvm_opts) + os.environ.get('JVM_OPTS', '')

    # Start Cassandra
    service = subprocess.Popen(['bin/cassandra', '-f'])
    signal.signal(signal.SIGTERM, lambda signum, frame: service.terminate())
    return service


generate_configs()
service = start_cassandra()

zk = advertise_zk(service)

try:
    service.communicate()
    service.wait()
finally:
    zk and zk.stop()
