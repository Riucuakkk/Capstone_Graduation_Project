{{ config(
    materialized='table',
    tags=['business_vault', 'customer']
) }}

with latest_customer_identity as {{ latest_by_key(
    'sat_customer_identity',
    'customer_hashkey',
    ['customer_unique_id']
) }}

select
    hc.customer_hashkey,
    hc.business_key as customer_id,
    lci.customer_unique_id,
    current_timestamp as bv_load_timestamp
from {{ ref('hub_customer') }} hc
left join latest_customer_identity lci
    on hc.customer_hashkey = lci.customer_hashkey
where lci.customer_unique_id is not null
