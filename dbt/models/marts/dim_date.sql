{{ config(materialized='table', tags=['mart', 'dim']) }}

select
    as_of_date_key as date_key,
    as_of_date as full_date,
    calendar_year,
    calendar_month,
    calendar_day,
    iso_weekday
from {{ ref('as_of_date') }}
