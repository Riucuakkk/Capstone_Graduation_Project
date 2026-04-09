{{ config(materialized='table', tags=['mart', 'fact', 'ml']) }}

select
    'category' as entity_type,
    category_key as entity_key,
    full_date,
    date_key,
    total_orders,
    total_items as total_units,
    total_gross_amount as total_revenue,
    current_timestamp as mart_load_timestamp
from {{ ref('fact_category_daily') }}

union all

select
    'seller' as entity_type,
    seller_key as entity_key,
    full_date,
    date_key,
    total_orders,
    total_items as total_units,
    total_gross_amount as total_revenue,
    current_timestamp as mart_load_timestamp
from {{ ref('fact_seller_daily') }}

union all

select
    'customer_state' as entity_type,
    customer_state as entity_key,
    full_date,
    date_key,
    total_orders,
    total_orders as total_units,
    total_revenue,
    current_timestamp as mart_load_timestamp
from {{ ref('fact_geo_daily') }}
