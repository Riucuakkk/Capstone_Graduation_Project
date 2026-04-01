{{ config(
    materialized='table',
    tags=['business_vault', 'bridge']
) }}

with latest_order_item_details as {{ latest_by_key(
    'sat_order_item_details',
    'order_product_seller_hashkey',
    ['order_item_id', 'shipping_limit_date', 'price', 'freight_value']
) }},
latest_product_details as {{ latest_by_key(
    'sat_product_details',
    'product_hashkey',
    [
        'product_category_name',
        'product_name_length',
        'product_description_length',
        'product_photos_qty',
        'product_weight_g',
        'product_length_cm',
        'product_height_cm',
        'product_width_cm'
    ]
) }},
latest_seller_address as {{ latest_by_key(
    'sat_seller_address',
    'seller_hashkey',
    ['seller_zip_code_prefix', 'seller_city', 'seller_state']
) }}

select
    ops.order_product_seller_hashkey,
    ops.order_hashkey,
    ho.business_key as order_id,
    pit.customer_hashkey,
    pit.customer_id,
    pit.customer_unique_id,
    ops.product_hashkey,
    hp.business_key as product_id,
    pd.product_category_name,
    pd.product_name_length,
    pd.product_description_length,
    pd.product_photos_qty,
    pd.product_weight_g,
    pd.product_length_cm,
    pd.product_height_cm,
    pd.product_width_cm,
    ops.seller_hashkey,
    hs.business_key as seller_id,
    sa.seller_zip_code_prefix,
    sa.seller_city,
    sa.seller_state,
    oi.order_item_id,
    oi.shipping_limit_date,
    oi.price,
    oi.freight_value,
    oi.price + oi.freight_value as gross_item_amount,
    pit.order_status,
    pit.order_purchase_timestamp,
    pit.order_approved_at,
    pit.order_delivered_carrier_date,
    pit.order_delivered_customer_date,
    pit.order_estimated_delivery_date,
    pit.approval_lead_hours,
    pit.delivery_cycle_days,
    pit.is_delivered_late,
    case
        when oi.shipping_limit_date is not null and pit.order_delivered_carrier_date is not null
             and pit.order_delivered_carrier_date::date > oi.shipping_limit_date::date
            then true
        when oi.shipping_limit_date is not null and pit.order_delivered_carrier_date is not null
            then false
    end as shipped_after_limit,
    current_timestamp as bv_load_timestamp
from {{ ref('lnk_order_product_seller') }} ops
left join latest_order_item_details oi
    on ops.order_product_seller_hashkey = oi.order_product_seller_hashkey
left join {{ ref('hub_order') }} ho
    on ops.order_hashkey = ho.order_hashkey
left join {{ ref('hub_product') }} hp
    on ops.product_hashkey = hp.product_hashkey
left join {{ ref('hub_seller') }} hs
    on ops.seller_hashkey = hs.seller_hashkey
left join latest_product_details pd
    on ops.product_hashkey = pd.product_hashkey
left join latest_seller_address sa
    on ops.seller_hashkey = sa.seller_hashkey
left join {{ ref('pit_order_snapshot') }} pit
    on ops.order_hashkey = pit.order_hashkey
