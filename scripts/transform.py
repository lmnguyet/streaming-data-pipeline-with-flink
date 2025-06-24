from pyflink.datastream import StreamExecutionEnvironment, CheckpointingMode
from pyflink.table import StreamTableEnvironment
from pyflink.table.catalog import ObjectPath

CATALOG_NAME = "hive_catalog"
KAFKA_SERVER = "kafka:9092"
INPUT_TOPIC = "source-orders"
OUTPUT_TOPIC = "sink-revenue-each-2-min"
INPUT_TABLE = "kafka_source_orders"
OUTPUT_TABLE = "kafka_sink_revenue_each_2_min"

ENV = StreamExecutionEnvironment.get_execution_environment()

TABLE_ENV = StreamTableEnvironment.create(ENV)

TABLE_ENV.get_config().set("pipeline.jars", "file:///opt/flink/lib/flink-sql-connector-kafka-3.3.0-1.20.jar")

TABLE_ENV.execute_sql(f"""
    CREATE CATALOG {CATALOG_NAME} WITH (
        'type' = 'hive',
        'hive-conf-dir' = '/opt/hive-conf'
    );
""")

TABLE_ENV.use_catalog(CATALOG_NAME)

def create_tables(input_table=INPUT_TABLE, output_table=OUTPUT_TABLE, input_topic=INPUT_TOPIC, output_topic=OUTPUT_TOPIC):
    if TABLE_ENV.get_catalog(CATALOG_NAME).table_exists(ObjectPath("default", input_table)):
        TABLE_ENV.execute_sql(f"""
            ALTER TABLE {input_table}
            SET ('scan.startup.mode' = 'group-offsets')
        """)

    TABLE_ENV.execute_sql(f"""
        CREATE TABLE IF NOT EXISTS {input_table} (
            order_id STRING,
            user_id INT,
            item STRING,
            quantity INT,
            unit_price DOUBLE,
            total_amount DOUBLE,
            payment_method STRING,
            location ROW<city STRING, country STRING>,
            event_time TIMESTAMP(3),
            WATERMARK FOR event_time AS event_time - INTERVAL '5' SECOND
        )
        WITH (
            'connector' = 'kafka',
            'topic' = '{input_topic}',
            'properties.bootstrap.servers' = '{KAFKA_SERVER}',
            'scan.startup.mode' = 'earliest-offset',
            'properties.group.id' = '{input_topic}-group',
            'format' = 'json',
            'json.timestamp-format.standard' = 'ISO-8601'
        );
    """)

    TABLE_ENV.execute_sql(f"""
        CREATE TABLE IF NOT EXISTS {output_table} (
            window_start TIMESTAMP(3),
            window_end TIMESTAMP(3),
            revenue DOUBLE
        )
        WITH (
            'connector' = 'kafka',
            'topic' = '{output_topic}',
            'properties.bootstrap.servers' = '{KAFKA_SERVER}',
            'format' = 'json',
            'json.timestamp-format.standard' = 'ISO-8601'
        );
    """)

def calc_revenue_2_min(input_table=INPUT_TABLE, output_table=OUTPUT_TABLE):
    TABLE_ENV.execute_sql(f"""
        INSERT INTO {output_table}
        SELECT order_id, user_id, event_time 
        FROM {input_table}
    """)

def main():
    create_tables()
    calc_revenue_2_min()

if __name__ == "__main__":
    main()