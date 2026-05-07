{{ config(materialized='table', tags=['mart', 'fact']) }}

select
    bol.order_product_seller_hashkey as order_item_key,
    bol.order_hashkey,
    bol.order_id,
    bol.customer_unique_id as customer_key,
    bol.product_id as product_key,
    bol.seller_id as seller_key,
    cast(to_char(bol.order_purchase_timestamp::date, 'YYYYMMDD') as text) as order_date_key,
    bol.order_purchase_timestamp,
    bol.order_item_id,
    bol.product_category_name,
    bpm.product_category_name_english,
    bol.seller_city,
    bol.seller_state,
    bol.price,
    bol.freight_value,
    bol.gross_item_amount,
    bol.product_weight_g,
    bol.product_length_cm,
    bol.product_height_cm,
    bol.product_width_cm,
    bol.order_status,
    bol.approval_lead_hours,
    bol.delivery_cycle_days,
    bol.is_delivered_late,
    bol.shipped_after_limit,
    current_timestamp as mart_load_timestamp
from {{ ref('bridge_order_line') }} bol
left join {{ ref('bridge_product_master') }} bpm
    on bol.product_hashkey = bpm.product_hashkey
