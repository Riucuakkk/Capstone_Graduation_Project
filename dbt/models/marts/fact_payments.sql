{{ config(materialized='table', tags=['mart', 'fact']) }}

with latest_payment_details as {{ latest_by_key(
    'sat_order_payment_details',
    'order_payment_hashkey',
    ['payment_type', 'payment_installments', 'payment_value']
) }}

select
    lop.order_payment_hashkey as payment_key,
    lop.order_hashkey,
    ho.business_key as order_id,
    pit.customer_unique_id as customer_key,
    cast(to_char(pit.order_purchase_timestamp::date, 'YYYYMMDD') as text) as order_date_key,
    opd.payment_type as payment_type_key,
    opd.payment_type,
    opd.payment_installments,
    opd.payment_value,
    current_timestamp as mart_load_timestamp
from {{ ref('lnk_order_payment') }} lop
left join latest_payment_details opd
    on lop.order_payment_hashkey = opd.order_payment_hashkey
left join {{ ref('hub_order') }} ho
    on lop.order_hashkey = ho.order_hashkey
left join {{ ref('bridge_order_current_snapshot') }} pit
    on lop.order_hashkey = pit.order_hashkey
