{{ config(materialized='view', tags=['mart', 'bi', 'superset']) }}

select
    ml_sample_key,
    product_key,
    date_key,
    full_date,
    coalesce(product_category, 'unknown') as product_category,
    coalesce(weight_band, 'unknown') as weight_band,
    calendar_month,
    calendar_day,
    iso_weekday,
    coalesce(total_items, 0) as historical_units,
    coalesce(total_orders, 0) as historical_orders,
    coalesce(total_gross_amount, 0) as historical_revenue,
    coalesce(total_freight_value, 0) as freight_value,
    delivered_late_ratio,
    coalesce(lag_1_total_items, 0) as lag_1_units,
    coalesce(lag_1_total_orders, 0) as lag_1_orders,
    coalesce(lag_1_total_gross_amount, 0) as lag_1_revenue,
    coalesce(trailing_7_sale_day_avg_items, 0) as trailing_7_sale_day_avg_units,
    coalesce(trailing_7_sale_day_avg_revenue, 0) as trailing_7_sale_day_avg_revenue,
    coalesce(next_7d_units, 0) as next_7d_units_signal,
    coalesce(next_7d_revenue, 0) as next_7d_revenue_signal,
    demand_quintile_next_7d,
    case when is_bestseller_next_7d then 1 else 0 end as bestseller_flag,
    case
        when is_bestseller_next_7d then 'Top demand next 7d'
        else 'Normal demand'
    end as bestseller_label,
    case
        when demand_quintile_next_7d = 1 then 'Q1 - top 20%'
        when demand_quintile_next_7d = 2 then 'Q2'
        when demand_quintile_next_7d = 3 then 'Q3'
        when demand_quintile_next_7d = 4 then 'Q4'
        when demand_quintile_next_7d = 5 then 'Q5 - bottom 20%'
        else 'unknown'
    end as demand_band,
    case
        when coalesce(total_items, 0) > 0 then coalesce(total_gross_amount, 0) / total_items
        else 0
    end as avg_revenue_per_unit,
    case
        when coalesce(total_items, 0) > 0 then coalesce(total_freight_value, 0) / total_items
        else 0
    end as avg_freight_per_unit
from {{ ref('fact_ml_product_demand') }}
