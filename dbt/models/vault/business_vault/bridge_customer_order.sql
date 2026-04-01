{{ config(
    materialized='table',
    tags=['business_vault', 'bridge']
) }}

with latest_review_details as {{ latest_by_key(
    'sat_review_details',
    'review_hashkey',
    [
        'review_score',
        'review_comment_title',
        'review_comment_message',
        'review_answer_timestamp'
    ]
) }},
review_summary as (
    select
        lor.order_hashkey,
        count(*) as review_count,
        avg(rd.review_score) as avg_review_score,
        max(rd.review_score) as max_review_score,
        min(rd.review_score) as min_review_score,
        max(case when coalesce(rd.review_comment_title, '') <> '' or coalesce(rd.review_comment_message, '') <> '' then 1 else 0 end) = 1 as has_review_comment,
        max(case when rd.review_answer_timestamp is not null then 1 else 0 end) = 1 as review_answered
    from {{ ref('lnk_order_review') }} lor
    left join latest_review_details rd
        on lor.review_hashkey = rd.review_hashkey
    group by lor.order_hashkey
)

select
    pit.customer_hashkey,
    pit.customer_id,
    pit.customer_unique_id,
    pit.customer_zip_code_prefix,
    pit.customer_city,
    pit.customer_state,
    min(pit.order_purchase_timestamp) as first_order_timestamp,
    max(pit.order_purchase_timestamp) as last_order_timestamp,
    count(distinct pit.order_hashkey) as total_orders,
    count(distinct case when pit.order_status = 'delivered' then pit.order_hashkey end) as delivered_orders,
    count(distinct case when pit.order_status = 'canceled' then pit.order_hashkey end) as canceled_orders,
    count(distinct case when pit.order_status = 'unavailable' then pit.order_hashkey end) as unavailable_orders,
    avg(pit.delivery_cycle_days) as avg_delivery_cycle_days,
    avg(case when pit.is_delivered_late then 1.0 else 0.0 end) as late_delivery_ratio,
    sum(coalesce(bop.total_payment_value, 0)) as total_customer_revenue,
    avg(bop.total_payment_value) as avg_order_value,
    avg(rs.avg_review_score) as avg_review_score,
    max(case when rs.has_review_comment then 1 else 0 end) = 1 as has_review_comment_history,
    current_timestamp as bv_load_timestamp
from {{ ref('pit_order_snapshot') }} pit
left join {{ ref('bridge_order_payment') }} bop
    on pit.order_hashkey = bop.order_hashkey
left join review_summary rs
    on pit.order_hashkey = rs.order_hashkey
group by
    pit.customer_hashkey,
    pit.customer_id,
    pit.customer_unique_id,
    pit.customer_zip_code_prefix,
    pit.customer_city,
    pit.customer_state
