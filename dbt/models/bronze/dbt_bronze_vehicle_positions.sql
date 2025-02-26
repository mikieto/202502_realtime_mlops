{{ config(
    materialized='table',
    alias='dbt_bronze_vehicle_positions'
) }}

-- PoC: Copy from the existing CSV table created by spark-sql
-- or simply select from it.
SELECT * FROM default.vehicle_positions

