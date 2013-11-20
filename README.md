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

  - `SERVICE_NAME` should contain the logical name of the service this
    container is an instance of;
  - `CONTAINER_NAME` should contain the logical name of the container,
    which will be used for looking up links and ports informations from the
    other environment variables. For this, the name is uppercased and
    non-alphanumeric characters are replaced by underscores;
  - `CONTAINER_HOST_ADDRESS` should contain the address of the Docker
    container's host. It's used by Cassandra's Gossip protocol as the
    advertised host name and is required for the container to start;

  - `CLUSTER_NAME`, the Cassandra cluster name, driving the
    `cluster_name` configuration setting. Defaults to `Cassandra
    cluster`;
  - `<SERVICE_NAME>_<CONTAINER_NAME>_STORAGE_PORT`, the storage command
    and data port (`storage_port` setting). Defaults to 7000;
  - `<SERVICE_NAME>_<CONTAINER_NAME>_TRANSPORT_PORT`, the native
    transport listening port (`native_transport_port` setting). Defaults
    to 9042;
  - `<SERVICE_NAME>_<CONTAINER_NAME>_RPC_PORT`, the Thrift RPC interface
    listening port (`rpc_port` setting). Defaults to 9160.

The peer list will be constructed from the `<SERVICE_NAME>_*_HOST` variables.

Volumes
-------

The Cassandra image uses the two following volumes that you may want to map
from the container's host:

  - `/var/lib/cassandra/data`, for Cassandra's data;
  - `/var/lib/cassandra/commitlog`, for the write logs.

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
