{{ config(materialized='table', tags=['mart', 'dim']) }}

select distinct
    coalesce(product_category_name, 'unknown') as product_category_key,
    product_category_name,
    coalesce(product_category_name_english, 'unknown') as product_category_name_english,
    current_timestamp as mart_load_timestamp
from {{ ref('bridge_product_master') }}
