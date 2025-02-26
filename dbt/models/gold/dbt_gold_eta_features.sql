{{ config(
    materialized='table',
    alias='dbt_gold_eta_features'
) }}

/*

This model calculates the estimated time of arrival (ETA) for each stop

*/

WITH base AS (
    SELECT
        vp.start_date,
        vp.trip_id,
        vp.current_stop_sequence,
        vp.arrival_time,
        vp.departure_time,
        vp.producer_timestamp_ts,

        to_utc_timestamp(
          to_timestamp(
            concat(CAST(vp.start_date AS STRING), ' ', date_format(st.scheduled_arrival_time, 'HH:mm:ss')),
            'yyyyMMdd HH:mm:ss'
          ),
          'Asia/Tokyo'
        ) AS scheduled_arrival_time,

        to_utc_timestamp(
          to_timestamp(
            concat(CAST(vp.start_date AS STRING), ' ', date_format(st.scheduled_departure_time, 'HH:mm:ss')),
            'yyyyMMdd HH:mm:ss'
          ),
          'Asia/Tokyo'
        ) AS scheduled_departure_time

    FROM {{ ref('dbt_silver_vehicle_positions') }} vp
    LEFT JOIN {{ ref('dbt_silver_stop_times') }} st
    ON vp.trip_id = st.trip_id
    AND vp.current_stop_sequence = st.stop_sequence
),

with_lead AS (
    SELECT
        start_date,
        trip_id,
        current_stop_sequence,
        arrival_time,
        departure_time,
        producer_timestamp_ts,
        scheduled_arrival_time,
        scheduled_departure_time,

        LEAD(arrival_time, 1)
            OVER (PARTITION BY start_date, trip_id ORDER BY current_stop_sequence) 
            AS next_arrival_time,

        LEAD(scheduled_arrival_time, 1)
            OVER (PARTITION BY start_date, trip_id ORDER BY current_stop_sequence)
            AS next_scheduled_arrival_time

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

    scheduled_arrival_time,
    scheduled_departure_time,
    next_scheduled_arrival_time,

    UNIX_TIMESTAMP(next_scheduled_arrival_time)
    -
    UNIX_TIMESTAMP(scheduled_arrival_time) AS scheduled_travel_time_second,

    UNIX_TIMESTAMP(
      to_timestamp(
        concat(start_date, ' ', date_format(scheduled_departure_time, 'HH:mm:ss')),
        'yyyyMMdd HH:mm:ss'
      )
    )
    - 
    UNIX_TIMESTAMP(departure_time) AS departure_delay_time_second,

    producer_timestamp_ts AS producer_timestamp

FROM with_lead
ORDER BY
    start_date,
    trip_id,
    current_stop_sequence
;
