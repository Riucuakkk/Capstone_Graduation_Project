{{ config(materialized='table', tags=['mart', 'fact']) }}

select
    fo.customer_key,
    fo.order_key,
    fo.order_hashkey,
    fo.order_date_key,
    fo.order_purchase_timestamp,
    fo.order_status,
    fo.total_payment_value,
    fo.total_items,
    fo.total_gross_amount,
    fo.delivery_cycle_days,
    fo.is_delivered_late,
    fo.avg_review_score,
    fo.service_quality_band,
    current_timestamp as mart_load_timestamp
from {{ ref('fact_orders') }} fo
where fo.customer_key is not null
