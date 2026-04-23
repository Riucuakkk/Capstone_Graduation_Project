{{ config(materialized='table', tags=['mart', 'fact', 'ml']) }}

with geo_features as (
    select
        coalesce(customer_state, 'unknown') as customer_state,
        coalesce(customer_city, 'unknown') as customer_city,
        date_key,
        full_date,
        extract(month from full_date)::int as calendar_month,
        extract(day from full_date)::int as calendar_day,
        extract(isodow from full_date)::int as iso_weekday,
        coalesce(total_orders, 0) as total_orders,
        coalesce(total_revenue, 0) as total_revenue,
        late_delivery_ratio,
        avg_review_score,
        lag(total_orders, 1) over (
            partition by customer_state, customer_city
            order by full_date
        ) as lag_1_total_orders,
        lag(total_revenue, 1) over (
            partition by customer_state, customer_city
            order by full_date
        ) as lag_1_total_revenue,
        avg(total_orders) over (
            partition by customer_state, customer_city
            order by full_date
            rows between 6 preceding and current row
        ) as trailing_7_sale_day_avg_orders,
        avg(total_revenue) over (
            partition by customer_state, customer_city
            order by full_date
            rows between 6 preceding and current row
        ) as trailing_7_sale_day_avg_revenue
    from {{ ref('fact_geo_daily') }}
),
geo_targets as (
    select
        gf.customer_state,
        gf.customer_city,
        gf.full_date,
        coalesce(sum(future.total_orders), 0) as next_7d_orders,
        coalesce(sum(future.total_revenue), 0) as next_7d_revenue
    from geo_features gf
    left join {{ ref('fact_geo_daily') }} future
        on gf.customer_state = coalesce(future.customer_state, 'unknown')
        and gf.customer_city = coalesce(future.customer_city, 'unknown')
        and future.full_date > gf.full_date
        and future.full_date <= gf.full_date + interval '7 days'
    group by
        gf.customer_state,
        gf.customer_city,
        gf.full_date
),
scored as (
    select
        gf.*,
        gt.next_7d_orders,
        gt.next_7d_revenue,
        ntile(5) over (
            partition by gf.full_date
            order by gt.next_7d_orders desc, gt.next_7d_revenue desc, gf.customer_state, gf.customer_city
        ) as geo_demand_quintile_next_7d
    from geo_features gf
    inner join geo_targets gt
        on gf.customer_state = gt.customer_state
        and gf.customer_city = gt.customer_city
        and gf.full_date = gt.full_date
)

select
    concat(customer_state, '_', customer_city, '_', date_key) as ml_sample_key,
    concat(customer_state, '|', customer_city) as location_key,
    customer_state,
    customer_city,
    date_key,
    full_date,
    calendar_month,
    calendar_day,
    iso_weekday,
    total_orders,
    total_revenue,
    late_delivery_ratio,
    avg_review_score,
    lag_1_total_orders,
    lag_1_total_revenue,
    trailing_7_sale_day_avg_orders,
    trailing_7_sale_day_avg_revenue,
    next_7d_orders,
    next_7d_revenue,
    geo_demand_quintile_next_7d,
    geo_demand_quintile_next_7d = 1 as is_high_demand_area_next_7d,
    current_timestamp as mart_load_timestamp
from scored
