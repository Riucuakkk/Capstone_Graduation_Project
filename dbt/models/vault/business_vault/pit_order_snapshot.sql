{{ config(
    materialized='table',
    tags=['business_vault', 'pit']
) }}

with latest_order_status as {{ latest_by_key(
    'sat_order_status',
    'order_hashkey',
    ['order_status', 'source_event_date as status_effective_at']
) }},
latest_order_timestamps as {{ latest_by_key(
    'sat_order_timestamps',
    'order_hashkey',
    [
        'order_purchase_timestamp',
        'order_approved_at',
        'order_delivered_carrier_date',
        'order_delivered_customer_date',
        'order_estimated_delivery_date'
    ]
) }},
order_customer as {{ latest_by_key(
    'lnk_order_customer',
    'order_hashkey',
    ['customer_hashkey']
) }},
customer_identity as {{ latest_by_key(
    'sat_customer_identity',
    'customer_hashkey',
    ['customer_unique_id']
) }},
customer_address as {{ latest_by_key(
    'sat_customer_address',
    'customer_hashkey',
    ['customer_zip_code_prefix', 'customer_city', 'customer_state']
) }}

select
    ho.order_hashkey,
    ho.business_key as order_id,
    oc.customer_hashkey,
    hc.business_key as customer_id,
    ci.customer_unique_id,
    ca.customer_zip_code_prefix,
    ca.customer_city,
    ca.customer_state,
    los.order_status,
    los.status_effective_at,
    lot.order_purchase_timestamp,
    lot.order_approved_at,
    lot.order_delivered_carrier_date,
    lot.order_delivered_customer_date,
    lot.order_estimated_delivery_date,
    case
        when lot.order_approved_at is not null and lot.order_purchase_timestamp is not null
            then extract(epoch from (lot.order_approved_at - lot.order_purchase_timestamp)) / 3600.0
    end as approval_lead_hours,
    case
        when lot.order_delivered_customer_date is not null and lot.order_purchase_timestamp is not null
            then extract(epoch from (lot.order_delivered_customer_date - lot.order_purchase_timestamp)) / 86400.0
    end as delivery_cycle_days,
    case
        when lot.order_delivered_customer_date is not null
             and lot.order_estimated_delivery_date is not null
             and lot.order_delivered_customer_date::date > lot.order_estimated_delivery_date::date
            then true
        when lot.order_delivered_customer_date is not null
             and lot.order_estimated_delivery_date is not null
            then false
    end as is_delivered_late,
    current_timestamp as bv_load_timestamp
from {{ ref('hub_order') }} ho
left join order_customer oc
    on ho.order_hashkey = oc.order_hashkey
left join {{ ref('hub_customer') }} hc
    on oc.customer_hashkey = hc.customer_hashkey
left join customer_identity ci
    on oc.customer_hashkey = ci.customer_hashkey
left join customer_address ca
    on oc.customer_hashkey = ca.customer_hashkey
left join latest_order_status los
    on ho.order_hashkey = los.order_hashkey
left join latest_order_timestamps lot
    on ho.order_hashkey = lot.order_hashkey
