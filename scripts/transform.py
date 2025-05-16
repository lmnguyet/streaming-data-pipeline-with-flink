from pyflink.table import EnvironmentSettings, TableEnvironment
from pyflink.table.catalog import HiveCatalog

env_settings = EnvironmentSettings.in_streaming_mode()
table_env = TableEnvironment.create(env_settings)

table_env.get_config().set("pipeline.jars", "file:///opt/flink/lib/flink-sql-connector-kafka-3.3.0-1.20.jar")

table_env.execute_sql("""
    CREATE CATALOG hive_catalog WITH (
        'type' = 'hive',
        'hive-conf-dir' = '/opt/hive-conf'
    );
""")

# catalogs = table_env.list_catalogs()

# print("Catalogs:")
# for cat in catalogs:
#     print(f" - {cat}")

# hive_catalog = HiveCatalog("hive_catalog", "default", "/opt/hive-conf")
# table_env.register_catalog("hive_catalog", hive_catalog)

# set the HiveCatalog as the current catalog of the session
table_env.use_catalog("hive_catalog")

print(table_env.get_current_catalog())
print(table_env.get_current_database())

# create input table
table_env.execute_sql("""
    CREATE TABLE IF NOT EXISTS kafka_orders (
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
        'topic' = 'orders',
        'properties.bootstrap.servers' = 'kafka:9092',
        'properties.group.id' = 'orders-input',
        'scan.startup.mode' = 'earliest-offset',
        'format' = 'json',
        'json.timestamp-format.standard' = 'ISO-8601'
    );
""")

# table = table_env.from_path("kafka_orders")
# table.execute().print()

# create output table
# table_env.execute_sql("""
#     CREATE TABLE IF NOT EXISTS revenue_each_5min (
#         window_start TIMESTAMP(3),
#         window_end TIMESTAMP(3),
#         revenue DOUBLE
#     ) WITH (
#         'connector' = 'filesystem',
#         'path' = 's3://warehouse/revenue_each_5min',
#         'format' = 'parquet'
#     );
# """)

# table_env.execute_sql("""
#     CREATE TABLE IF NOT EXISTS order_count_10sec (
#         window_start TIMESTAMP(3),
#         window_end TIMESTAMP(3),
#         revenue DOUBLE
#     ) WITH (
#         'connector' = 'filesystem',
#         'path' = 's3://warehouse/order_count_10sec',
#         'format' = 'parquet'
#     );
# """)

# read from input, transform and insert to output
# table_env.execute_sql("""
#     INSERT INTO revenue_each_5min
#     SELECT
#         TUMBLE_START(event_time, INTERVAL '5' MINUTE) AS window_start,
#         TUMBLE_END(event_time, INTERVAL '5' MINUTE) AS window_end,
#         SUM(total_amount) AS revenue
#     FROM orders
#     GROUP BY TUMBLE(event_time, INTERVAL '5' MINUTE);
# """)

# table_env.execute_sql("""
#     INSERT INTO order_count_10sec
#     SELECT
#         HOP_START(event_time, INTERVAL '10' SECOND, INTERVAL '1' MINUTE) AS window_start,
#         HOP_START(event_time, INTERVAL '10' SECOND, INTERVAL '1' MINUTE) AS window_end,
#         COUNT(*) AS order_count
#     FROM orders
#     GROUP BY HOP(event_time, INTERVAL '10' SECOND, INTERVAL '1' MINUTE);
# """)


