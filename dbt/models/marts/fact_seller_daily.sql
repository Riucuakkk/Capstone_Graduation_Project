{{ config(materialized='table', tags=['mart', 'fact']) }}

select
    seller_key,
    cast(to_char(order_purchase_timestamp::date, 'YYYYMMDD') as text) as date_key,
    order_purchase_timestamp::date as full_date,
    count(*) as total_items,
    count(distinct order_id) as total_orders,
    sum(coalesce(gross_item_amount, 0)) as total_gross_amount,
    sum(coalesce(freight_value, 0)) as total_freight_value,
    avg(case when shipped_after_limit then 1.0 else 0.0 end) as shipped_after_limit_ratio,
    avg(case when is_delivered_late then 1.0 else 0.0 end) as delivered_late_ratio,
    current_timestamp as mart_load_timestamp
from {{ ref('fact_order_items') }}
group by
    seller_key,
    cast(to_char(order_purchase_timestamp::date, 'YYYYMMDD') as text),
    order_purchase_timestamp::date
