{{ config(
    materialized='table',
    alias='dbt_gold_eta_features'
) }}

/*

This model calculates the estimated time of arrival (ETA) for each stop

*/

WITH base AS (
    SELECT
        start_date,
        trip_id,
        current_stop_sequence,
        arrival_time,
        departure_time,
        producer_timestamp_ts

    FROM {{ ref('dbt_silver_vehicle_positions') }}
),

with_lead AS (
    SELECT
        start_date,
        trip_id,
        current_stop_sequence,
        arrival_time,
        departure_time,
        producer_timestamp_ts,

        LEAD(arrival_time, 1)
          OVER (
            PARTITION BY start_date, trip_id
            ORDER BY current_stop_sequence
          ) AS next_arrival_time

    FROM base
)

SELECT
    start_date,
    trip_id,
    current_stop_sequence,
    arrival_time,
    departure_time,
    next_arrival_time,

    UNIX_TIMESTAMP(next_arrival_time) 
    - 
    UNIX_TIMESTAMP(arrival_time) AS travel_time_second,

    producer_timestamp_ts

FROM with_lead
ORDER BY
    start_date,
    trip_id,
    current_stop_sequence
;
