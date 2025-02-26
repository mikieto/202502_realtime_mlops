-- dbt/models/bronze/dbt_bronze_stops.sql

{{ config(
    materialized='table',
    alias='dbt_bronze_stops'
) }}

-- PoC: Copy from the existing CSV table created by spark-sql
-- or simply select from it.
SELECT * FROM default.stops
