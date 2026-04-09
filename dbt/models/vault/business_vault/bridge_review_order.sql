{{ config(
    materialized='table',
    tags=['business_vault', 'review']
) }}

with latest_review_details as {{ latest_by_key(
    'sat_review_details',
    'review_hashkey',
    [
        'review_score',
        'review_comment_title',
        'review_comment_message',
        'review_creation_date',
        'review_answer_timestamp'
    ]
) }}

select
    lor.order_review_hashkey,
    lor.order_hashkey,
    ho.business_key as order_id,
    lor.review_hashkey,
    hr.business_key as review_id,
    pit.customer_hashkey,
    pit.customer_id,
    pit.customer_unique_id,
    rd.review_score,
    rd.review_creation_date,
    rd.review_answer_timestamp,
    coalesce(rd.review_comment_title, '') as review_comment_title,
    coalesce(rd.review_comment_message, '') as review_comment_message,
    (coalesce(rd.review_comment_title, '') <> '' or coalesce(rd.review_comment_message, '') <> '') as has_review_comment,
    case
        when rd.review_score <= 2 then 'low'
        when rd.review_score = 3 then 'neutral'
        when rd.review_score >= 4 then 'high'
    end as review_band,
    case
        when rd.review_answer_timestamp is not null and rd.review_creation_date is not null
            then extract(epoch from (rd.review_answer_timestamp - rd.review_creation_date)) / 3600.0
    end as review_answer_hours,
    case
        when rd.review_creation_date is not null and pit.order_delivered_customer_date is not null
            then extract(epoch from (rd.review_creation_date - pit.order_delivered_customer_date)) / 86400.0
    end as days_to_review_after_delivery,
    current_timestamp as bv_load_timestamp
from {{ ref('lnk_order_review') }} lor
left join latest_review_details rd
    on lor.review_hashkey = rd.review_hashkey
left join {{ ref('hub_order') }} ho
    on lor.order_hashkey = ho.order_hashkey
left join {{ ref('hub_review') }} hr
    on lor.review_hashkey = hr.review_hashkey
left join {{ ref('bridge_order_current_snapshot') }} pit
    on lor.order_hashkey = pit.order_hashkey
