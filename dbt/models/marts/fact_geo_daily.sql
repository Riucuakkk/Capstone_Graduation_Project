{{ config(materialized='table', tags=['mart', 'fact']) }}

select
    pit.customer_state,
    pit.customer_city,
    cast(to_char(pit.order_purchase_timestamp::date, 'YYYYMMDD') as text) as date_key,
    pit.order_purchase_timestamp::date as full_date,
    count(*) as total_orders,
    sum(coalesce(total_payment_value, 0)) as total_revenue,
    avg(case when is_delivered_late then 1.0 else 0.0 end) as late_delivery_ratio,
    avg(avg_review_score) as avg_review_score,
    current_timestamp as mart_load_timestamp
from {{ ref('bridge_order_current_snapshot') }} pit
left join {{ ref('fact_orders') }} fo
    on pit.order_hashkey = fo.order_hashkey
group by
    pit.customer_state,
    pit.customer_city,
    cast(to_char(pit.order_purchase_timestamp::date, 'YYYYMMDD') as text),
    pit.order_purchase_timestamp::date
