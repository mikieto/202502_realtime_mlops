#!/usr/bin/env bash
set -eux

echo "=== Creating Spark Tables via beeline ==="
beeline -u "jdbc:hive2://spark-thrift:10000/default" -n spark -p "" -e "
  USE default;
  CREATE TABLE IF NOT EXISTS vehicle_positions 
    USING DELTA LOCATION 's3a://my-bucket/delta-lake';

  CREATE TABLE IF NOT EXISTS stop_times
    USING CSV
    OPTIONS (
      path 's3a://my-bucket/bronze/gtfs_data/stop_times.txt',
      header='true',
      inferSchema='true'
    );

  CREATE TABLE IF NOT EXISTS stops
    USING CSV
    OPTIONS (
      path 's3a://my-bucket/bronze/gtfs_data/stops.txt',
      header='true',
      inferSchema='true'
    );
"

echo "=== Initialization complete ==="



