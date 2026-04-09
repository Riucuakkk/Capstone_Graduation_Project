{{ config(materialized='table', tags=['mart', 'fact']) }}

select
    fco.customer_key,
    date_trunc('month', fco.order_purchase_timestamp)::date as month_start_date,
    to_char(date_trunc('month', fco.order_purchase_timestamp), 'YYYYMM') as month_key,
    count(*) as total_orders,
    sum(coalesce(fco.total_payment_value, 0)) as total_revenue,
    avg(fco.total_payment_value) as avg_order_value,
    avg(case when fco.is_delivered_late then 1.0 else 0.0 end) as late_delivery_ratio,
    avg(fco.avg_review_score) as avg_review_score,
    current_timestamp as mart_load_timestamp
from {{ ref('fact_customer_orders') }} fco
group by
    fco.customer_key,
    date_trunc('month', fco.order_purchase_timestamp)::date,
    to_char(date_trunc('month', fco.order_purchase_timestamp), 'YYYYMM')
