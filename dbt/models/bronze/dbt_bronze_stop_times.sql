-- dbt/models/bronze/dbt_bronze_stop_times.sql

{{ config(
    materialized='table',
    alias='dbt_bronze_stop_times'
) }}

-- PoC: Copy from the existing CSV table created by spark-sql
-- or simply select from it.
SELECT * FROM default.stop_times

