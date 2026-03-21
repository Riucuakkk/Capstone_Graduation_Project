{{ config(
    materialized='view'
) }}

{% set source_name = 'source' %}
{% set source_table = 'sellers' %}
{% set source_date_col = none %}
{% set business_key_cols = ['seller_id'] %}

{% set hashdiff_satellite_dict = {
    'hashdiff_seller_address': ['seller_zip_code_prefix', 'seller_city', 'seller_state']
} %}

{{ staging(
    source_name=source_name,
    source_table=source_table,
    source_date_col=source_date_col,
    business_key_cols=business_key_cols,
    hashdiff_satellite_dict=hashdiff_satellite_dict
) }}