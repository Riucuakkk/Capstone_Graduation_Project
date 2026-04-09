{{ config(materialized='table', tags=['mart', 'dim']) }}

select distinct
    order_status as order_status_key,
    order_status,
    case
        when order_status in ('approved', 'processing', 'shipped', 'invoiced') then 'active'
        when order_status = 'delivered' then 'completed'
        when order_status in ('canceled', 'unavailable') then 'failed'
        else 'other'
    end as order_status_group,
    current_timestamp as mart_load_timestamp
from {{ ref('v_stg_source_orders') }}
where order_status is not null
