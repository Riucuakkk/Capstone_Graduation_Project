{{ config(
    materialized = 'incremental',
    incremental_strategy = 'merge',
    unique_key = ['product_hashkey', 'hashdiff'],
    skip_matched_step = true,
    auto_liquid_cluster = true,
    tags = ['source']
) }}

{% set source_name = 'source' %}
{% set source_table = 'products' %}
{% set hashdiff_col = 'hashdiff_product_details' %}
{% set hub_hashkey = 'product_hashkey' %}
{% set source_model = 'v_stg_source_products' %}
{% set list_cols = [
    'product_category_name',
    'product_name_length',
    'product_description_length',
    'product_photos_qty',
    'product_weight_g',
    'product_length_cm',
    'product_height_cm',
    'product_width_cm'
] %}
{% set raw_sql %}
    {{ sat(
        source_model=source_model,
        source_name=source_name,
        source_table=source_table,
        hub_hashkey=hub_hashkey,
        hashdiff_name=hashdiff_col,
        list_cols=list_cols
    ) }}
{% endset %}

{% if not is_incremental() %}
    {{ raw_sql }}
{% else %}
    {{ satellite(raw_sql, hub_hashkey, source_name ~ '__' ~ source_table) }}
{% endif %}