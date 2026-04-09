{{ config(materialized='table', tags=['mart', 'fact', 'prediction']) }}

select
    cast(null as text) as order_key,
    cast(null as timestamp) as prediction_timestamp,
    cast(null as text) as model_name,
    cast(null as text) as model_version,
    cast(null as numeric) as score,
    cast(null as text) as predicted_class,
    cast(null as text) as risk_band,
    cast(null as text) as top_reason_1,
    cast(null as text) as top_reason_2,
    cast(null as text) as top_reason_3,
    cast(null as text) as recommended_action
where 1 = 0
