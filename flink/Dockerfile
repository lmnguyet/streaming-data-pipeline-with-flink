FROM flink:1.20.1-scala_2.12

COPY ./lib/*.jar /opt/flink/lib/

RUN mkdir /opt/flink/plugins/s3-fs-hadoop
COPY ./plugins/flink-s3-fs-hadoop-1.20.1.jar /opt/flink/plugins/s3-fs-hadoop/

RUN apt-get update -y && \
apt-get install -y python3 python3-pip python3-dev && rm -rf /var/lib/apt/lists/*
RUN ln -s /usr/bin/python3 /usr/bin/python

RUN pip3 install apache-flink==1.20.1
