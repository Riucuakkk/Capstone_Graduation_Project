{{ config(
    materialized='table',
    tags=['business_vault', 'customer']
) }}

with review_summary as (
    select
        bro.order_hashkey,
        avg(bro.review_score) as avg_review_score,
        max(case when bro.has_review_comment then 1 else 0 end) = 1 as has_review_comment,
        max(case when bro.review_score <= 2 then 1 else 0 end) = 1 as has_low_review
    from {{ ref('bridge_review_order') }} bro
    group by bro.order_hashkey
),
customer_orders as (
    select
        bci.customer_unique_id,
        pit.customer_hashkey,
        pit.customer_id,
        pit.order_hashkey,
        pit.order_status,
        pit.order_purchase_timestamp,
        pit.order_delivered_customer_date,
        pit.delivery_cycle_days,
        pit.is_delivered_late,
        bop.total_payment_value,
        bop.payment_transaction_count,
        rs.avg_review_score,
        rs.has_review_comment,
        rs.has_low_review
    from {{ ref('bridge_order_current_snapshot') }} pit
    inner join {{ ref('bridge_customer_identity') }} bci
        on pit.customer_hashkey = bci.customer_hashkey
    left join {{ ref('bridge_order_payment') }} bop
        on pit.order_hashkey = bop.order_hashkey
    left join review_summary rs
        on pit.order_hashkey = rs.order_hashkey
),
latest_customer_location as (
    select
        customer_unique_id,
        customer_hashkey,
        customer_id,
        customer_city,
        customer_state,
        customer_zip_code_prefix
    from (
        select
            bci.customer_unique_id,
            pit.customer_hashkey,
            pit.customer_id,
            pit.customer_city,
            pit.customer_state,
            pit.customer_zip_code_prefix,
            row_number() over (
                partition by bci.customer_unique_id
                order by pit.order_purchase_timestamp desc nulls last, pit.order_id desc
            ) as rn
        from {{ ref('bridge_order_current_snapshot') }} pit
        inner join {{ ref('bridge_customer_identity') }} bci
            on pit.customer_hashkey = bci.customer_hashkey
    ) ranked
    where rn = 1
)

select
    sac.customer_unique_id,
    sac.canonical_customer_hashkey as customer_hashkey,
    sac.canonical_customer_id as customer_id,
    sac.customer_id_count,
    lcl.customer_city,
    lcl.customer_state,
    lcl.customer_zip_code_prefix,
    min(co.order_purchase_timestamp) as first_order_timestamp,
    max(co.order_purchase_timestamp) as last_order_timestamp,
    count(distinct co.order_hashkey) as total_orders,
    count(distinct case when co.order_status = 'delivered' then co.order_hashkey end) as delivered_orders,
    count(distinct case when co.order_status = 'canceled' then co.order_hashkey end) as canceled_orders,
    count(distinct case when co.order_status = 'unavailable' then co.order_hashkey end) as unavailable_orders,
    sum(coalesce(co.total_payment_value, 0)) as total_customer_revenue,
    avg(co.total_payment_value) as avg_order_value,
    avg(co.delivery_cycle_days) as avg_delivery_cycle_days,
    avg(case when co.is_delivered_late then 1.0 else 0.0 end) as late_delivery_ratio,
    avg(co.avg_review_score) as avg_review_score,
    max(case when co.has_review_comment then 1 else 0 end) = 1 as has_review_comment_history,
    max(case when co.has_low_review then 1 else 0 end) = 1 as has_low_review_history,
    current_timestamp as bv_load_timestamp
from {{ ref('same_as_customer') }} sac
left join customer_orders co
    on sac.customer_unique_id = co.customer_unique_id
left join latest_customer_location lcl
    on sac.customer_unique_id = lcl.customer_unique_id
group by
    sac.customer_unique_id,
    sac.canonical_customer_hashkey,
    sac.canonical_customer_id,
    sac.customer_id_count,
    lcl.customer_city,
    lcl.customer_state,
    lcl.customer_zip_code_prefix
