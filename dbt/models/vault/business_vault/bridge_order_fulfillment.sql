{{ config(
    materialized='table',
    tags=['business_vault', 'order']
) }}

select
    bol.order_hashkey,
    bol.order_id,
    min(bol.order_purchase_timestamp) as order_purchase_timestamp,
    count(*) as total_items,
    count(distinct bol.product_id) as distinct_products,
    count(distinct bol.seller_id) as distinct_sellers,
    sum(coalesce(bol.price, 0)) as total_item_price,
    sum(coalesce(bol.freight_value, 0)) as total_freight_value,
    sum(coalesce(bol.gross_item_amount, 0)) as total_gross_amount,
    avg(bol.product_weight_g) as avg_product_weight_g,
    sum(coalesce(bol.product_weight_g, 0)) as total_product_weight_g,
    max(case when bol.shipped_after_limit then 1 else 0 end) = 1 as has_shipped_after_limit,
    avg(case when bol.shipped_after_limit then 1.0 else 0.0 end) as shipped_after_limit_ratio,
    avg(case when bol.is_delivered_late then 1.0 else 0.0 end) as delivered_late_ratio,
    current_timestamp as bv_load_timestamp
from {{ ref('bridge_order_line') }} bol
group by
    bol.order_hashkey,
    bol.order_id
