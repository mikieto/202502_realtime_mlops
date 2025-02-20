{{ config(
    materialized='table',
    alias='dbt_gold_eta_features'
) }}

-- 
-- This model represents the Gold layer for ETA features.
-- Since there are no master tables to join at this time, this model simply
-- passes through the data from the silver layer.
--
-- The silver layer table "dbt_silver_intermediate_vehicle_positions" contains
-- the cleaned and formatted vehicle position data with proper timestamp conversions.
-- Future transformations or feature engineering for ETA predictions can be added here.
--

SELECT *
FROM {{ ref('silver_intermediate') }}
