{{ config(materialized='table', tags=['mart', 'fact', 'ml']) }}

with product_features as (
    select
        fpd.product_key,
        fpd.date_key,
        fpd.full_date,
        coalesce(dp.product_category_name_english, dp.product_category_name, 'unknown') as product_category,
        dp.product_name_length,
        dp.product_description_length,
        dp.product_photos_qty,
        dp.product_weight_g,
        dp.product_length_cm,
        dp.product_height_cm,
        dp.product_width_cm,
        dp.weight_band,
        extract(month from fpd.full_date)::int as calendar_month,
        extract(day from fpd.full_date)::int as calendar_day,
        extract(isodow from fpd.full_date)::int as iso_weekday,
        fpd.total_items,
        fpd.total_orders,
        fpd.total_gross_amount,
        fpd.total_freight_value,
        fpd.delivered_late_ratio,
        lag(fpd.total_items, 1) over (
            partition by fpd.product_key
            order by fpd.full_date
        ) as lag_1_total_items,
        lag(fpd.total_orders, 1) over (
            partition by fpd.product_key
            order by fpd.full_date
        ) as lag_1_total_orders,
        lag(fpd.total_gross_amount, 1) over (
            partition by fpd.product_key
            order by fpd.full_date
        ) as lag_1_total_gross_amount,
        avg(fpd.total_items) over (
            partition by fpd.product_key
            order by fpd.full_date
            rows between 6 preceding and current row
        ) as trailing_7_sale_day_avg_items,
        avg(fpd.total_gross_amount) over (
            partition by fpd.product_key
            order by fpd.full_date
            rows between 6 preceding and current row
        ) as trailing_7_sale_day_avg_revenue
    from {{ ref('fact_product_daily') }} fpd
    left join {{ ref('dim_products') }} dp
        on fpd.product_key = dp.product_key
),
product_targets as (
    select
        pf.product_key,
        pf.full_date,
        coalesce(sum(future.total_items), 0) as next_7d_units,
        coalesce(sum(future.total_gross_amount), 0) as next_7d_revenue
    from product_features pf
    left join {{ ref('fact_product_daily') }} future
        on pf.product_key = future.product_key
        and future.full_date > pf.full_date
        and future.full_date <= pf.full_date + interval '7 days'
    group by
        pf.product_key,
        pf.full_date
),
scored as (
    select
        pf.*,
        pt.next_7d_units,
        pt.next_7d_revenue,
        ntile(5) over (
            partition by pf.full_date
            order by pt.next_7d_units desc, pt.next_7d_revenue desc, pf.product_key
        ) as demand_quintile_next_7d
    from product_features pf
    inner join product_targets pt
        on pf.product_key = pt.product_key
        and pf.full_date = pt.full_date
)

select
    concat(product_key, '_', date_key) as ml_sample_key,
    product_key,
    date_key,
    full_date,
    product_category,
    product_name_length,
    product_description_length,
    product_photos_qty,
    product_weight_g,
    product_length_cm,
    product_height_cm,
    product_width_cm,
    weight_band,
    calendar_month,
    calendar_day,
    iso_weekday,
    total_items,
    total_orders,
    total_gross_amount,
    total_freight_value,
    delivered_late_ratio,
    lag_1_total_items,
    lag_1_total_orders,
    lag_1_total_gross_amount,
    trailing_7_sale_day_avg_items,
    trailing_7_sale_day_avg_revenue,
    next_7d_units,
    next_7d_revenue,
    demand_quintile_next_7d,
    demand_quintile_next_7d = 1 as is_bestseller_next_7d,
    current_timestamp as mart_load_timestamp
from scored
