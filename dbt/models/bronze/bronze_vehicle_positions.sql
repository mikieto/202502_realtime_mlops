{{ config(
    materialized='table',
    alias='dbt_bronze_vehicle_positions'
) }}

-- 
-- This model ingests raw vehicle position data from the source table 
-- "vehicle_positions" (created by the init_tables.sh script)
-- and stores it as a Bronze layer table with minimal transformation.
--
-- Columns in vehicle_positions:
--   gtfs_realtime_version (string)
--   incrementality        (string)
--   feed_timestamp        (string)
--   producer_timestamp    (double)
--   source_id             (string)
--   event_type            (string)
--   entity_id             (string)
--   trip_id               (string)
--   start_date            (string)
--   schedule_relationship (string)
--   latitude              (double)
--   longitude             (double)
--   current_stop_sequence (string)
--   current_status        (string)
--   vehicle_timestamp_str (string)
--   vehicle_id            (string)
--   processing_timestamp  (timestamp)
--

SELECT
    gtfs_realtime_version,
    incrementality,
    feed_timestamp,
    producer_timestamp,
    source_id,
    event_type,
    entity_id,
    trip_id,
    start_date,
    schedule_relationship,
    latitude,
    longitude,
    current_stop_sequence,
    current_status,
    vehicle_timestamp_str,
    vehicle_id,
    processing_timestamp
FROM default.vehicle_positions
