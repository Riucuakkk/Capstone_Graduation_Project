{{ config(materialized='table', tags=['mart', 'dim']) }}

select
    seller_id as seller_key,
    seller_hashkey,
    seller_zip_code_prefix,
    seller_city,
    seller_state,
    first_order_timestamp,
    last_order_timestamp,
    total_orders,
    total_items,
    total_gross_item_amount,
    avg_item_amount,
    shipped_after_limit_ratio,
    delivered_late_ratio,
    case
        when coalesce(delivered_late_ratio, 0) >= 0.3 then 'high_risk'
        when coalesce(delivered_late_ratio, 0) >= 0.15 then 'medium_risk'
        else 'low_risk'
    end as seller_risk_band,
    current_timestamp as mart_load_timestamp
from {{ ref('bridge_seller_master') }}
