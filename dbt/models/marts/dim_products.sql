{{ config(materialized='table', tags=['mart', 'dim']) }}

select
    product_id as product_key,
    product_hashkey,
    product_category_name,
    product_category_name_english,
    product_name_length,
    product_description_length,
    product_photos_qty,
    product_weight_g,
    product_length_cm,
    product_height_cm,
    product_width_cm,
    case
        when product_weight_g >= 5000 then 'heavy'
        when product_weight_g >= 1000 then 'medium'
        else 'light'
    end as weight_band,
    current_timestamp as mart_load_timestamp
from {{ ref('bridge_product_master') }}
