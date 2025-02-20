{{ config(
    materialized='table',
    alias='dbt_silver_intermediate_vehicle_positions'
) }}

-- 
-- This model takes the raw vehicle position data from the Bronze layer,
-- cleans and formats the timestamp fields, and produces an intermediate ("Silver")
-- table for further transformations and analysis.
--
-- Expected columns in dbt_bronze_vehicle_positions:
--   gtfs_realtime_version   (string)
--   incrementality          (string)
--   feed_timestamp          (string)   e.g., '2023-02-19 12:00:00'
--   producer_timestamp      (double)   Unix epoch seconds
--   source_id               (string)
--   event_type              (string)
--   entity_id               (string)
--   trip_id                 (string)
--   start_date              (string)
--   schedule_relationship   (string)
--   latitude                (double)
--   longitude               (double)
--   current_stop_sequence   (string)
--   current_status          (string)
--   vehicle_timestamp_str   (string)   e.g., '2023-02-19 12:00:05'
--   vehicle_id              (string)
--   processing_timestamp    (timestamp)
--

WITH raw AS (
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
    FROM {{ ref('bronze_vehicle_positions') }}
)

SELECT
    gtfs_realtime_version,
    incrementality,
    -- Convert feed_timestamp from string to timestamp.
    from_unixtime(CAST(feed_timestamp AS string)) AS feed_timestamp_ts,
    -- Convert producer_timestamp (Unix epoch seconds) to timestamp.
    from_unixtime(cast(producer_timestamp as BIGINT)) AS producer_timestamp_ts, 
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
    -- Convert vehicle_timestamp_str from string to timestamp.
    from_unixtime(CAST(vehicle_timestamp_str AS string)) AS vehicle_timestamp_str_ts,
    vehicle_id,
    processing_timestamp
FROM raw
