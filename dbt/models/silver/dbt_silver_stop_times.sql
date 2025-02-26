{{ config(
    materialized='table',
    alias='dbt_silver_stop_times'
) }}

WITH raw AS (
    SELECT
        trip_id,
        CAST(stop_sequence AS int) AS stop_sequence,

        -- Convert arrival_time to actual timestamp
        CAST(
          from_unixtime(
            CAST(
              SUBSTR(arrival_time, 1, 2)*3600
              + SUBSTR(arrival_time, 4, 2)*60
              + SUBSTR(arrival_time, 7, 2)
              AS BIGINT
            )
          )
          AS timestamp
        ) AS scheduled_arrival_time_ts,

        -- Convert departure_time to actual timestamp
        CAST(
          from_unixtime(
            CAST(
              SUBSTR(departure_time, 1, 2)*3600
              + SUBSTR(departure_time, 4, 2)*60
              + SUBSTR(departure_time, 7, 2)
              AS BIGINT
            )
          )
          AS timestamp
        ) AS scheduled_departure_time_ts,

        stop_id
    FROM {{ ref('dbt_bronze_stop_times') }}
)

SELECT
    trip_id,
    stop_sequence,
    scheduled_arrival_time_ts,
    scheduled_departure_time_ts,
    stop_id
FROM raw;
