{{ config(materialized='table', tags=['mart', 'fact']) }}

select
    coalesce(product_category_name_english, product_category_name, 'unknown') as category_key,
    cast(to_char(order_purchase_timestamp::date, 'YYYYMMDD') as text) as date_key,
    order_purchase_timestamp::date as full_date,
    count(*) as total_items,
    count(distinct order_id) as total_orders,
    sum(coalesce(gross_item_amount, 0)) as total_gross_amount,
    avg(case when is_delivered_late then 1.0 else 0.0 end) as delivered_late_ratio,
    current_timestamp as mart_load_timestamp
from {{ ref('fact_order_items') }}
group by
    coalesce(product_category_name_english, product_category_name, 'unknown'),
    cast(to_char(order_purchase_timestamp::date, 'YYYYMMDD') as text),
    order_purchase_timestamp::date
