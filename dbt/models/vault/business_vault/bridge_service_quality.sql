{{ config(
    materialized='table',
    tags=['business_vault', 'quality']
) }}

with review_agg as (
    select
        bro.order_hashkey,
        count(*) as review_count,
        avg(bro.review_score) as avg_review_score,
        min(bro.review_score) as min_review_score,
        max(bro.review_score) as max_review_score,
        max(case when bro.has_review_comment then 1 else 0 end) = 1 as has_review_comment,
        avg(bro.review_answer_hours) as avg_review_answer_hours,
        avg(bro.days_to_review_after_delivery) as avg_days_to_review_after_delivery
    from {{ ref('bridge_review_order') }} bro
    group by bro.order_hashkey
)

select
    ol.order_hashkey,
    ol.order_id,
    ol.customer_hashkey,
    ol.customer_id,
    ol.customer_unique_id,
    ol.order_status,
    ol.is_delivered,
    ol.is_canceled,
    ol.delivery_cycle_days,
    ol.delivery_delay_days,
    ol.is_delivered_late,
    bop.total_payment_value,
    bop.has_installments,
    bop.dominant_payment_type,
    ra.review_count,
    ra.avg_review_score,
    ra.min_review_score,
    ra.max_review_score,
    ra.has_review_comment,
    ra.avg_review_answer_hours,
    ra.avg_days_to_review_after_delivery,
    case
        when ra.avg_review_score <= 2 then true
        else false
    end as is_low_review_order,
    case
        when ol.is_delivered_late then 'delivery_risk'
        when ra.avg_review_score <= 2 then 'service_risk'
        when ol.is_canceled then 'cancellation_risk'
        else 'normal'
    end as service_quality_band,
    current_timestamp as bv_load_timestamp
from {{ ref('bridge_order_lifecycle') }} ol
left join {{ ref('bridge_order_payment') }} bop
    on ol.order_hashkey = bop.order_hashkey
left join review_agg ra
    on ol.order_hashkey = ra.order_hashkey
