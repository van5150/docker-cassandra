# Dockerfile for Cassandra

FROM quay.io/signalfuse/maestro-base:0.1.6
MAINTAINER Maxime Petazzoni <max@signalfuse.com>

ENV DEBIAN_FRONTEND noninteractive

# Python YAML is needed to tweak Cassandra's configuration
RUN apt-get update
RUN apt-get -y install python-yaml

# Get the latest stable version of Cassandra
RUN wget -q -O - http://archive.apache.org/dist/cassandra/2.0.7/apache-cassandra-2.0.7-bin.tar.gz \
  | tar -C /opt -xz

ADD jmxagent.jar /opt/apache-cassandra-2.0.7/lib/
ADD run.py /opt/apache-cassandra-2.0.7/.docker/

WORKDIR /opt/apache-cassandra-2.0.7
VOLUME /var/lib/cassandra/data
VOLUME /var/lib/cassandra/commitlog
VOLUME /var/log/cassandra
CMD ["python", "/opt/apache-cassandra-2.0.7/.docker/run.py"]
