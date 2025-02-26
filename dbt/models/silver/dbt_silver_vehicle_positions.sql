{{ config(
    materialized='table',
    alias='dbt_silver_vehicle_positions'
) }}

/*
In Bronze table, there may be multiple rows for the same (start_date, trip_id, current_stop_sequence)
(e.g., slightly different timestamps). This model groups them and aggregates them into 1 row
by taking the minimum vehicle_timestamp_ts as arrival_time and the maximum vehicle_timestamp_ts as departure_time.
Also, it converts producer_timestamp (double) to TIMESTAMP and vehicle_timestamp_str (string) to TIMESTAMP.
*/


-- Step 1) Convert producer_timestamp / vehicle_timestamp_str to TIMESTAMP
WITH raw AS (
    SELECT
        -- Columns carried over from Bronze
        gtfs_realtime_version,
        incrementality,
        feed_timestamp,
        source_id,
        event_type,
        entity_id,
        trip_id,
        start_date,
        schedule_relationship,
        latitude,
        longitude,
        -- Convert current_stop_sequence (string) to INT
        CAST(current_stop_sequence AS INT) AS current_stop_sequence,
        current_status,
        vehicle_id,
        processing_timestamp,

        -- Convert producer_timestamp (double) to TIMESTAMP
        CAST(
          FROM_UNIXTIME(
            CAST(producer_timestamp AS BIGINT)
          ) AS TIMESTAMP
        ) AS producer_timestamp_ts,

        -- Convert vehicle_timestamp_str (string) to TIMESTAMP
        CAST(
          FROM_UNIXTIME(
            CAST(vehicle_timestamp_str AS BIGINT)
          ) AS TIMESTAMP
        ) AS vehicle_timestamp_ts

    FROM {{ ref('dbt_bronze_vehicle_positions') }}
),

-- Step 2) Group by (start_date, trip_id, current_stop_sequence)
--         and compute MIN(...) as arrival_time, MAX(...) as departure_time
grouped AS (
    SELECT
        start_date,
        trip_id,
        current_stop_sequence,

        -- arrival_time = minimum of vehicle_timestamp_ts
        MIN(vehicle_timestamp_ts) AS arrival_time,
        -- departure_time = maximum of vehicle_timestamp_ts
        MAX(vehicle_timestamp_ts) AS departure_time,
        -- producer_timestamp_ts = maximum of producer_timestamp_ts
        MAX(producer_timestamp_ts) AS producer_timestamp_ts

    FROM raw
    GROUP BY
        start_date,
        trip_id,
        current_stop_sequence
)

SELECT
    -- aggregated columns
    start_date,
    trip_id,
    current_stop_sequence,
    -- result columns
    arrival_time,
    departure_time,
    producer_timestamp_ts

FROM grouped
ORDER BY start_date, trip_id, current_stop_sequence
;