#!/usr/bin/env python3
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, current_timestamp, explode
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, ArrayType, LongType, TimestampType, DoubleType

# Import configuration values from streaming_config.py
from streaming_config import KAFKA_BROKER, KAFKA_TOPIC, DELTA_LAKE_PATH, CHECKPOINT_DIR

# Create a Spark session with Kafka and Delta Lake support
spark = (
    SparkSession.builder
        .appName("RealTimeETL")
        .config(
            "spark.jars.packages",
            "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1,io.delta:delta-core_2.12:2.4.0"
        )
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        .config("spark.sql.execution.arrow.pyspark.enabled", "true") \
        .getOrCreate()
)

# Define the schema for the incoming JSON data based on the actual structure.
# The JSON structure includes:
# - a "header" field (with version, incrementality, and a feed timestamp),
# - an "entity" array (each with its own id and a nested "vehicle" object),
# - and top-level metadata: "producer_timestamp", "source_id", and "event_type".
schema = StructType([
    StructField("header", StructType([
        StructField("gtfs_realtime_version", StringType(), True),
        StructField("incrementality", StringType(), True),
        # feed timestamp is provided as a string in the JSON
        StructField("timestamp", StringType(), True)
    ]), True),
    StructField("entity", ArrayType(
        StructType([
            StructField("id", StringType(), True),
            StructField("vehicle", StructType([
                StructField("trip", StructType([
                    StructField("trip_id", StringType(), True),
                    StructField("start_date", StringType(), True),
                    StructField("schedule_relationship", StringType(), True)
                ]), True),
                StructField("position", StructType([
                    StructField("latitude", DoubleType(), True),
                    StructField("longitude", DoubleType(), True)
                ]), True),
                # current_stop_sequence and current_status are read as strings;
                # you may change these to IntegerType() if you prefer
                StructField("current_stop_sequence", StringType(), True),
                StructField("current_status", StringType(), True),
                # vehicle timestamp as string
                StructField("timestamp", StringType(), True),
                StructField("vehicle", StructType([
                    StructField("id", StringType(), True)
                ]), True)
            ]), True)
            # "trip_update" field exists in the JSON but is null; it is omitted here.
        ])
    ), True),
    StructField("producer_timestamp", DoubleType(), True),
    StructField("source_id", StringType(), True),
    StructField("event_type", StringType(), True)
])

# Read streaming data from Kafka
kafka_df = (
    spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", KAFKA_BROKER)
        .option("subscribe", KAFKA_TOPIC)
        .option("startingOffsets", "latest")
        .load()
)

# Convert the binary 'value' column to a string and parse the JSON using the defined schema.
raw_df = kafka_df.selectExpr("CAST(value AS STRING) as json_str")
parsed_df = raw_df.select(from_json(col("json_str"), schema).alias("data"))

# Flatten the JSON structure by selecting the top-level metadata and the nested "entity" array.
flattened_df = parsed_df.select(
    col("data.header.gtfs_realtime_version").alias("gtfs_realtime_version"),
    col("data.header.incrementality").alias("incrementality"),
    col("data.header.timestamp").alias("feed_timestamp"),
    col("data.producer_timestamp").alias("producer_timestamp"),
    col("data.source_id").alias("source_id"),
    col("data.event_type").alias("event_type"),
    col("data.entity").alias("entity")
)

# Explode the "entity" array so that each entity becomes a separate row.
exploded_df = flattened_df.select(
    "*",
    explode(col("entity")).alias("entity_exploded")
)

# Select and rename fields from the exploded entity to flatten the nested structure.
final_df = exploded_df.select(
    "gtfs_realtime_version",
    "incrementality",
    "feed_timestamp",
    "producer_timestamp",
    "source_id",
    "event_type",
    col("entity_exploded.id").alias("entity_id"),
    col("entity_exploded.vehicle.trip.trip_id").alias("trip_id"),
    col("entity_exploded.vehicle.trip.start_date").alias("start_date"),
    col("entity_exploded.vehicle.trip.schedule_relationship").alias("schedule_relationship"),
    col("entity_exploded.vehicle.position.latitude").alias("latitude"),
    col("entity_exploded.vehicle.position.longitude").alias("longitude"),
    col("entity_exploded.vehicle.current_stop_sequence").alias("current_stop_sequence"),
    col("entity_exploded.vehicle.current_status").alias("current_status"),
    col("entity_exploded.vehicle.timestamp").alias("vehicle_timestamp_str"),
    col("entity_exploded.vehicle.vehicle.id").alias("vehicle_id")
)

# Add a processing time column to track when the record is processed.
final_df = final_df.withColumn("processing_timestamp", current_timestamp())

# For debugging: write the final flattened DataFrame to the console.
console_query = final_df.writeStream \
    .format("console") \
    .outputMode("append") \
    .option("truncate", "false") \
    .start()

# Write the processed data to Delta Lake with checkpointing.
delta_query = final_df.writeStream \
    .format("delta") \
    .option("checkpointLocation", CHECKPOINT_DIR) \
    .option("mergeSchema", "true") \
    .outputMode("append") \
    .start(DELTA_LAKE_PATH)

# Wait for the console query to run for a while (e.g., 30 seconds), then wait for the Delta query.
console_query.awaitTermination(30)
delta_query.awaitTermination()
