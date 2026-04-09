{{ config(materialized='table', tags=['mart', 'fact', 'ml']) }}

select
    order_item_key,
    order_id as order_key,
    customer_key,
    product_key,
    seller_key,
    order_date_key as snapshot_date_key,
    order_purchase_timestamp::date as snapshot_date,
    price,
    freight_value,
    gross_item_amount,
    product_weight_g,
    product_length_cm,
    product_height_cm,
    product_width_cm,
    approval_lead_hours,
    delivery_cycle_days,
    shipped_after_limit,
    is_delivered_late,
    current_timestamp as mart_load_timestamp
from {{ ref('fact_order_items') }}
