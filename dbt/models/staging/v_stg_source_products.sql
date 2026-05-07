{{ config(
    materialized='view'
) }}

{% set source_name = 'source' %}
{% set source_table = 'products' %}
{% set source_date_col = none %}
{% set business_key_cols = ['product_id'] %}

{% set hashdiff_satellite_dict = {
    'hashdiff_product_details': ['product_category_name', 'product_name_length', 'product_description_length', 'product_photos_qty', 'product_weight_g', 'product_length_cm', 'product_height_cm', 'product_width_cm']  
} %}

{{ staging(
    source_name=source_name,
    source_table=source_table,
    source_date_col=source_date_col,
    business_key_cols=business_key_cols,
    hashdiff_satellite_dict=hashdiff_satellite_dict
) }}