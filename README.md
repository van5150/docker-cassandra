Cassandra on Docker
===================

This `Dockerfile` creates a Docker image that can be used as the base for
running Cassandra within a Docker container. The run script is responsible
for creating the Cassandra configuration based on the container's
environment and starting the Cassandra service.

The version of Cassandra used is defined in the `Dockerfile` and generally
points to the latest stable release of Cassandra.

Environment variables
---------------------

The following environment variables are understood by the startup script to
seed the service's configuration:

  - `CASSANDRA_CONFIG_CLUSTER_NAME`, the Cassandra cluster name, driving the
    `cluster_name` configuration setting. Defaults to `Cassandra cluster`;
  - `CASSANDRA_CONFIG_DATA_DIRS`, a comma-separated list of data directories to
    be used by Cassandra (`data_file_directories`). Defaults to
    `/var/lib/cassandra/data`;
  - `CASSANDRA_CONFIG_COMMITLOG_DIR`, the commit log directory for Cassandra's
    write log (`commitlog_directory`). Defaults to
    `/var/lib/cassandra/commitlog`;
  - `CASSANDRA_CONFIG_BROADCAST_ADDRESS`, the address Cassandra should
    advertise to the other Cassandra nodes via the Gossip protocol. This should
    be an IP address accessible from outside the container that eventually
    forwards to the Cassandra ports. Defaults to `127.0.0.1`;
  - `CASSANDRA_CONFIG_SEED_PEERS`, a comma-separated list of seed peers for
    Cassandra to connect to for the first Gossip exchange(s). Defaults to
    `127.0.0.1` as well;
  - `CASSANDRA_CONFIG_STORAGE_PORT`, the storage command and data port
    (`storage_port` setting). Defaults to 7000;
  - `CASSANDRA_CONFIG_TRANSPORT_PORT`, the native transport listening port
    (`native_transport_port` setting). Defaults to 9042;
  - `CASSANDRA_CONFIG_RPC_PORT`, the Thrift RPC interface listening port
    (`rpc_port` setting). Defaults to 9160.

Usage
-----

To build a new image, simply run from this directory:

```
$ docker build -t `whoami`/cassandra:2.0.1 .
```

The Docker image will be built and now available for Docker to start a new
container from:

```
$ docker images | grep cassandra
mpetazzoni/cassandra       2.0.1               77eea03c7af9        20 hours ago        12.29 kB (virtual 941 MB)
```
