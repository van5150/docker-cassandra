# Dockerfile for Cassandra

FROM mpetazzoni/sf-base

MAINTAINER Maxime Petazzoni <max@signalfuse.com>

# Python YAML is needed to tweak Cassandra's configuration
RUN apt-get update
RUN apt-get -y install python python-yaml

# Get the latest stable version of Cassandra
RUN wget -q -O - http://www.gtlib.gatech.edu/pub/apache/cassandra/2.0.1/apache-cassandra-2.0.1-bin.tar.gz \
  | tar -C /opt -xz

ADD run.py /opt/apache-cassandra-2.0.1/.docker/

WORKDIR /opt/apache-cassandra-2.0.1
CMD ["python", "/opt/apache-cassandra-2.0.1/.docker/run.py"]
