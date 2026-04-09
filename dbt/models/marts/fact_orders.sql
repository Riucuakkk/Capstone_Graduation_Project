{{ config(materialized='table', tags=['mart', 'fact']) }}

select
    ol.order_id as order_key,
    ol.order_hashkey,
    ol.customer_unique_id as customer_key,
    ol.customer_id,
    cast(to_char(ol.order_purchase_timestamp::date, 'YYYYMMDD') as text) as order_date_key,
    ol.order_purchase_timestamp,
    ol.order_status,
    ol.is_approved,
    ol.is_shipped,
    ol.is_delivered,
    ol.is_canceled,
    ol.is_unavailable,
    ol.approval_lead_hours,
    ol.approval_to_carrier_hours,
    ol.carrier_to_customer_days,
    ol.delivery_cycle_days,
    ol.delivery_delay_days,
    ol.is_delivered_late,
    ofu.total_items,
    ofu.distinct_products,
    ofu.distinct_sellers,
    ofu.total_item_price,
    ofu.total_freight_value,
    ofu.total_gross_amount,
    bop.payment_transaction_count,
    bop.distinct_payment_type_count,
    bop.total_payment_value,
    bop.avg_payment_value,
    bop.max_payment_installments,
    bop.has_installments,
    bop.uses_credit_card,
    bop.uses_voucher,
    bop.dominant_payment_type,
    sq.review_count,
    sq.avg_review_score,
    sq.has_review_comment,
    sq.is_low_review_order,
    sq.service_quality_band,
    current_timestamp as mart_load_timestamp
from {{ ref('bridge_order_lifecycle') }} ol
left join {{ ref('bridge_order_fulfillment') }} ofu
    on ol.order_hashkey = ofu.order_hashkey
left join {{ ref('bridge_order_payment') }} bop
    on ol.order_hashkey = bop.order_hashkey
left join {{ ref('bridge_service_quality') }} sq
    on ol.order_hashkey = sq.order_hashkey
