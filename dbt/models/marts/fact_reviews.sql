{{ config(materialized='table', tags=['mart', 'fact']) }}

select
    bro.order_review_hashkey as review_event_key,
    bro.review_id as review_key,
    bro.order_id as order_key,
    bro.customer_unique_id as customer_key,
    cast(to_char(bro.review_creation_date::date, 'YYYYMMDD') as text) as review_date_key,
    bro.review_creation_date,
    bro.review_score,
    bro.review_band,
    bro.has_review_comment,
    bro.review_answer_hours,
    bro.days_to_review_after_delivery,
    sq.service_quality_band,
    sq.is_low_review_order,
    current_timestamp as mart_load_timestamp
from {{ ref('bridge_review_order') }} bro
left join {{ ref('bridge_service_quality') }} sq
    on bro.order_hashkey = sq.order_hashkey
