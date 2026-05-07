{{ config(
    materialized='table',
    tags=['business_vault', 'seller']
) }}

with latest_seller_address as {{ latest_by_key(
    'sat_seller_address',
    'seller_hashkey',
    ['seller_zip_code_prefix', 'seller_city', 'seller_state']
) }},
seller_item_stats as (
    select
        seller_hashkey,
        min(order_purchase_timestamp) as first_order_timestamp,
        max(order_purchase_timestamp) as last_order_timestamp,
        count(distinct order_hashkey) as total_orders,
        count(*) as total_items,
        sum(coalesce(gross_item_amount, 0)) as total_gross_item_amount,
        avg(gross_item_amount) as avg_item_amount,
        avg(case when shipped_after_limit then 1.0 else 0.0 end) as shipped_after_limit_ratio,
        avg(case when is_delivered_late then 1.0 else 0.0 end) as delivered_late_ratio
    from {{ ref('bridge_order_line') }}
    group by seller_hashkey
)

select
    hs.seller_hashkey,
    hs.business_key as seller_id,
    lsa.seller_zip_code_prefix,
    lsa.seller_city,
    lsa.seller_state,
    sis.first_order_timestamp,
    sis.last_order_timestamp,
    coalesce(sis.total_orders, 0) as total_orders,
    coalesce(sis.total_items, 0) as total_items,
    coalesce(sis.total_gross_item_amount, 0) as total_gross_item_amount,
    sis.avg_item_amount,
    sis.shipped_after_limit_ratio,
    sis.delivered_late_ratio,
    current_timestamp as bv_load_timestamp
from {{ ref('hub_seller') }} hs
left join latest_seller_address lsa
    on hs.seller_hashkey = lsa.seller_hashkey
left join seller_item_stats sis
    on hs.seller_hashkey = sis.seller_hashkey
