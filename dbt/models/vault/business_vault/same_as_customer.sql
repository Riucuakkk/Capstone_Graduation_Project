{{ config(
    materialized='table',
    tags=['business_vault', 'customer']
) }}

select
    customer_unique_id,
    min(customer_hashkey) as canonical_customer_hashkey,
    min(customer_id) as canonical_customer_id,
    count(distinct customer_id) as customer_id_count,
    current_timestamp as bv_load_timestamp
from {{ ref('bridge_customer_identity') }}
group by customer_unique_id
