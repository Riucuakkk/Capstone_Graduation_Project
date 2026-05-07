{{ config(materialized='table', tags=['mart', 'dim']) }}

select
    customer_unique_id as customer_key,
    customer_hashkey,
    customer_id as canonical_customer_id,
    customer_id_count,
    customer_city,
    customer_state,
    customer_zip_code_prefix,
    first_order_timestamp,
    last_order_timestamp,
    total_orders,
    delivered_orders,
    canceled_orders,
    unavailable_orders,
    total_customer_revenue,
    avg_order_value,
    avg_delivery_cycle_days,
    late_delivery_ratio,
    avg_review_score,
    has_review_comment_history,
    has_low_review_history,
    case
        when total_customer_revenue >= 1000 then 'high'
        when total_customer_revenue >= 300 then 'medium'
        else 'low'
    end as customer_value_segment,
    current_timestamp as mart_load_timestamp
from {{ ref('bridge_customer_profile') }}
