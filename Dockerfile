# Dockerfile for Cassandra

FROM mpetazzoni/maestro-base

MAINTAINER Maxime Petazzoni <max@signalfuse.com>

# Python YAML is needed to tweak Cassandra's configuration
RUN apt-get update
RUN apt-get -y install python python-yaml python-setuptools

# Install Maestro for guest utils
RUN easy_install http://github.com/signalfuse/maestro-ng/archive/maestro-0.1.0.zip

# Get the latest stable version of Cassandra
RUN wget -q -O - http://www.gtlib.gatech.edu/pub/apache/cassandra/2.0.1/apache-cassandra-2.0.1-bin.tar.gz \
  | tar -C /opt -xz

ADD run.py /opt/apache-cassandra-2.0.1/.docker/

WORKDIR /opt/apache-cassandra-2.0.1
VOLUME /var/lib/cassandra/data
VOLUME /var/lib/cassandra/commitlog
CMD ["python", "/opt/apache-cassandra-2.0.1/.docker/run.py"]
