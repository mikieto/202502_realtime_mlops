#!/usr/bin/env bash

beeline -u "jdbc:hive2://localhost:10000/default" \
  -e "USE default; \
    CREATE TABLE IF NOT EXISTS vehicle_positions USING DELTA LOCATION 's3a://my-bucket/delta-lake';"
