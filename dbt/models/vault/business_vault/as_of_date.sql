{{ config(
    materialized='table',
    tags=['control']
) }}

with source_dates as (
    select cast(order_purchase_timestamp as date) as as_of_date
    from {{ source('source', 'orders') }}
    where order_purchase_timestamp is not null

    union

    select cast(shipping_limit_date as date) as as_of_date
    from {{ source('source', 'order_items') }}
    where shipping_limit_date is not null

    union

    select cast(review_creation_date as date) as as_of_date
    from {{ source('source', 'order_reviews') }}
    where review_creation_date is not null

    union

    select cast(data_date as date) as as_of_date
    from {{ source('source', 'exchange_rates') }}
    where data_date is not null
),
date_bounds as (
    select
        min(as_of_date) as min_as_of_date,
        max(as_of_date) as max_as_of_date
    from source_dates
),
calendar as (
    select
        gs::date as as_of_date
    from date_bounds,
    generate_series(
        min_as_of_date,
        greatest(max_as_of_date, current_date),
        interval '1 day'
    ) as gs
)

select
    to_char(as_of_date, 'YYYYMMDD') as as_of_date_key,
    as_of_date,
    extract(year from as_of_date) as calendar_year,
    extract(month from as_of_date) as calendar_month,
    extract(day from as_of_date) as calendar_day,
    extract(isodow from as_of_date) as iso_weekday
from calendar
