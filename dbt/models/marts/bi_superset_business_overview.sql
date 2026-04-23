{{ config(materialized='view', tags=['mart', 'bi', 'superset']) }}

with daily_orders as (
    select
        order_purchase_timestamp::date as metric_date,
        count(*) as orders,
        sum(coalesce(total_payment_value, 0)) as revenue,
        avg(coalesce(total_payment_value, 0)) as avg_order_value,
        avg(case when is_delivered then 1.0 else 0.0 end) as delivered_rate,
        avg(case when is_canceled or is_unavailable then 1.0 else 0.0 end) as not_successful_rate,
        avg(coalesce(approval_lead_hours, 0)) as avg_approval_hours
    from {{ ref('fact_orders') }}
    where order_purchase_timestamp is not null
    group by order_purchase_timestamp::date
),
product_signal as (
    select
        full_date as metric_date,
        sum(case when is_bestseller_next_7d then 1 else 0 end) as bestseller_product_rows,
        sum(coalesce(next_7d_units, 0)) as next_7d_product_units_signal,
        sum(coalesce(next_7d_revenue, 0)) as next_7d_product_revenue_signal
    from {{ ref('fact_ml_product_demand') }}
    group by full_date
),
geo_signal as (
    select
        full_date as metric_date,
        sum(case when is_high_demand_area_next_7d then 1 else 0 end) as high_demand_area_rows,
        sum(coalesce(next_7d_orders, 0)) as next_7d_geo_orders_signal,
        sum(coalesce(next_7d_revenue, 0)) as next_7d_geo_revenue_signal
    from {{ ref('fact_ml_geo_demand') }}
    group by full_date
),
calendar_spine as (
    select metric_date from daily_orders
    union
    select metric_date from product_signal
    union
    select metric_date from geo_signal
)

select
    cs.metric_date,
    cast(to_char(cs.metric_date, 'YYYYMMDD') as text) as metric_date_key,
    coalesce(do.orders, 0) as orders,
    coalesce(do.revenue, 0) as revenue,
    coalesce(do.avg_order_value, 0) as avg_order_value,
    coalesce(do.delivered_rate, 0) as delivered_rate,
    coalesce(do.not_successful_rate, 0) as not_successful_rate,
    coalesce(do.avg_approval_hours, 0) as avg_approval_hours,
    coalesce(ps.bestseller_product_rows, 0) as bestseller_product_rows,
    coalesce(ps.next_7d_product_units_signal, 0) as next_7d_product_units_signal,
    coalesce(ps.next_7d_product_revenue_signal, 0) as next_7d_product_revenue_signal,
    coalesce(gs.high_demand_area_rows, 0) as high_demand_area_rows,
    coalesce(gs.next_7d_geo_orders_signal, 0) as next_7d_geo_orders_signal,
    coalesce(gs.next_7d_geo_revenue_signal, 0) as next_7d_geo_revenue_signal
from calendar_spine cs
left join daily_orders do
    on cs.metric_date = do.metric_date
left join product_signal ps
    on cs.metric_date = ps.metric_date
left join geo_signal gs
    on cs.metric_date = gs.metric_date
