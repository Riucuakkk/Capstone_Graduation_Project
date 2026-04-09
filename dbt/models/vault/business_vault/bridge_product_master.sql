{{ config(
    materialized='table',
    tags=['business_vault', 'product']
) }}

with latest_product_details as {{ latest_by_key(
    'sat_product_details',
    'product_hashkey',
    [
        'product_category_name',
        'product_name_length',
        'product_description_length',
        'product_photos_qty',
        'product_weight_g',
        'product_length_cm',
        'product_height_cm',
        'product_width_cm'
    ]
) }},
category_translation as (
    select
        product_category_name,
        product_category_name_english
    from (
        select
            product_category_name,
            product_category_name_english,
            row_number() over (
                partition by product_category_name
                order by product_category_name
            ) as rn
        from {{ ref('v_stg_source_product_category_name_translation') }}
        where product_category_name is not null
    ) ranked
    where rn = 1
)

select
    hp.product_hashkey,
    hp.business_key as product_id,
    lpd.product_category_name,
    ct.product_category_name_english,
    lpd.product_name_length,
    lpd.product_description_length,
    lpd.product_photos_qty,
    lpd.product_weight_g,
    lpd.product_length_cm,
    lpd.product_height_cm,
    lpd.product_width_cm,
    current_timestamp as bv_load_timestamp
from {{ ref('hub_product') }} hp
left join latest_product_details lpd
    on hp.product_hashkey = lpd.product_hashkey
left join category_translation ct
    on lpd.product_category_name = ct.product_category_name
