{{ config(materialized='view', tags=['mart', 'bi', 'superset']) }}

select
    ml_sample_key,
    location_key,
    coalesce(customer_state, 'unknown') as customer_state,
    coalesce(customer_city, 'unknown') as customer_city,
    date_key,
    full_date,
    calendar_month,
    calendar_day,
    iso_weekday,
    coalesce(total_orders, 0) as historical_orders,
    coalesce(total_revenue, 0) as historical_revenue,
    late_delivery_ratio,
    avg_review_score,
    coalesce(lag_1_total_orders, 0) as lag_1_orders,
    coalesce(lag_1_total_revenue, 0) as lag_1_revenue,
    coalesce(trailing_7_sale_day_avg_orders, 0) as trailing_7_sale_day_avg_orders,
    coalesce(trailing_7_sale_day_avg_revenue, 0) as trailing_7_sale_day_avg_revenue,
    coalesce(next_7d_orders, 0) as next_7d_orders_signal,
    coalesce(next_7d_revenue, 0) as next_7d_revenue_signal,
    geo_demand_quintile_next_7d,
    case when is_high_demand_area_next_7d then 1 else 0 end as high_demand_area_flag,
    case
        when is_high_demand_area_next_7d then 'High demand next 7d'
        else 'Normal demand'
    end as geo_demand_label,
    case
        when geo_demand_quintile_next_7d = 1 then 'Q1 - top 20%'
        when geo_demand_quintile_next_7d = 2 then 'Q2'
        when geo_demand_quintile_next_7d = 3 then 'Q3'
        when geo_demand_quintile_next_7d = 4 then 'Q4'
        when geo_demand_quintile_next_7d = 5 then 'Q5 - bottom 20%'
        else 'unknown'
    end as geo_demand_band,
    case
        when coalesce(total_orders, 0) > 0 then coalesce(total_revenue, 0) / total_orders
        else 0
    end as avg_revenue_per_order
from {{ ref('fact_ml_geo_demand') }}
