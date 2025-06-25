# Streaming Data Pipeline With Flink And Kafka
A **Docker-based** data pipeline to ingest and synchronize real-time data from **Kafka** to **ClickHouse** using **Flink** as compute engine.

**Read the detailed article at:** [Streaming Data Pipeline With Flink and Kafka]()

![]()

**What have been done in this pipeline**
- Simulating the generating real-time data process and ingesting them into a Kafka topic.
- Transforming real-time data with Flink and transferring them into another Kafka topic.
- Synchronizing transformed data with a ClickHouse database via Kafka Connect.
- Applying Hive Catalog for Flink tables to manage their schemas.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)

## Prerequisites
WSL version: 2.4.12.0

Docker version: 28.0.2

[Referring: Installing Docker on WSL](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository)

## Installation
1. Clone the repository

```
$ git clone https://github.com/lmnguyet/streaming-data-pipeline-with-flink.git
```

2. Build images, create network and volumes

```
$ docker build -t producer-img ./producer
$ docker build -t kafka-connect-img:3.0 ./kafka-connect
$ docker build -t flink-img:1.20.1 ./flink
```

```
$ docker network create stream-net
```

```
$ docker volume create zookeeper_volume && \
docker volume create kafka_volume && \
docker volume create mysql_volume && \
docker volume create minio_volume && \
docker volume create clickhouse_volume
```

3. Start the services

```
$ docker compose up -d [service names]
```

Run Flink SQL Client to interact with Flink CLI:

```
$ docker compose run --rm --name sql-client sql-client
```

Run ClickHouse Client to interact with ClickHouse database:

```
$ docker exec -it clickhouse clickhouse-client --host localhost --port 9000 --user [your username] --password [your password] --database [your database]
```

## Usage
**1. Generating real-time data into Kafka**

```
$ docker compose up -d zookeeper kafka kafka-ui
```

Create a topic to store source data:

```
docker exec -it kafka kafka-topics.sh --bootstrap-server kafka:9092 --create --topic source-orders
```

Generate random data and push them into the topic ```source-orders``` in JSON format:

```
$ docker compose up -d producer
```

**2. Transformating with Flink and Hive Catalog**

Create a sink topic to store the transformation results:

```
$ docker exec -it kafka kafka-topics.sh --bootstrap-server kafka:9092 --create --topic sink-revenue-each-2-min
```

Start Hive Metastore and Flink:

```
$ docker compose up -d mysql hive-metastore minio
$ docker compose up -d jobmanager taskmanager
```

Run a Flink job to do the transformation and write data into the Kafka topic ```sink-revenue-each-2-min```

```
docker exec -it jobmanager python jobs/transform.py
```

You can check the results at Kafka UI: ```http://localhost:9089```

Or, check the Flink tables at Flink CLI:

```
Flink SQL> create catalog hive_catalog with (
  'type' = 'hive',
  'hive-conf-dir' = '/opt/hive-conf'
);

Flink SQL> use catalog hive_catalog;

Flink SQL> show tables;
+-------------------------------+
|                    table name |
+-------------------------------+
| kafka_sink_revenue_each_2_min |
|           kafka_source_orders |
+-------------------------------+
```

**3. Synchronizing Kafka topic with ClickHouse database via Kafka Connect**

```
$ docker compose up -d clickhouse kafka-connect
```

In ClickHouse CLI, create a sink table with appropriate schema:

```
create table if not exists revenue_each_2_min (
    window_start DateTime64(3),
    window_end DateTime64(3),
    revenue Float64
) engine = MergeTree()
order by window_start;
```

Create a Kafka Connector from Kafka to ClickHouse:

```
$ curl -i -X POST -H "Accept:application/json" -H "Content-Type:application/json" localhost:8083/connectors/ -d @kafka-connect/clickhouse-connector.json
```

List the created connectors and the status of them:

```
$ curl -H "Accept:application/json" localhost:8083/connectors/
["clickhouse-connector"]

$ curl -s http://localhost:8083/connectors/clickhouse-connect/status | jq
```
