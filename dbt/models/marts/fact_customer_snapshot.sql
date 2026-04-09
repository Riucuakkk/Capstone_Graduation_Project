{{ config(materialized='table', tags=['mart', 'fact', 'ml']) }}

with customer_order_events as (
    select
        customer_key,
        order_purchase_timestamp::date as snapshot_date,
        order_key,
        total_payment_value,
        avg_review_score,
        case when is_delivered_late then 1 else 0 end as is_delivered_late_flag
    from {{ ref('fact_customer_orders') }}
),
ranked as (
    select
        customer_key,
        snapshot_date,
        order_key,
        row_number() over (
            partition by customer_key
            order by snapshot_date, order_key
        ) as order_sequence_number,
        count(*) over (
            partition by customer_key
            order by snapshot_date, order_key
            rows between unbounded preceding and current row
        ) as cumulative_orders,
        sum(coalesce(total_payment_value, 0)) over (
            partition by customer_key
            order by snapshot_date, order_key
            rows between unbounded preceding and current row
        ) as cumulative_revenue,
        avg(avg_review_score) over (
            partition by customer_key
            order by snapshot_date, order_key
            rows between unbounded preceding and current row
        ) as cumulative_avg_review_score,
        avg(is_delivered_late_flag::float) over (
            partition by customer_key
            order by snapshot_date, order_key
            rows between unbounded preceding and current row
        ) as cumulative_late_delivery_ratio,
        lag(snapshot_date) over (
            partition by customer_key
            order by snapshot_date, order_key
        ) as previous_snapshot_date
    from customer_order_events
)

select
    customer_key,
    cast(to_char(snapshot_date, 'YYYYMMDD') as text) as snapshot_date_key,
    snapshot_date,
    order_key as anchor_order_key,
    order_sequence_number,
    cumulative_orders,
    cumulative_revenue,
    case
        when cumulative_orders > 0 then cumulative_revenue / cumulative_orders
    end as cumulative_avg_order_value,
    cumulative_avg_review_score,
    cumulative_late_delivery_ratio,
    case
        when previous_snapshot_date is not null then snapshot_date - previous_snapshot_date
    end as days_since_previous_order,
    current_timestamp as mart_load_timestamp
from ranked
