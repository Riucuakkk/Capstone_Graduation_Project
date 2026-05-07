{{ config(
    materialized='view'
)}}

{% set source_name = 'source' %}
{% set source_table = 'customers' %}
{% set source_date_col = none %}    
{% set business_key_cols = ['customer_id'] %}

{% set hashdiff_satellite_dict = {
    'hashdiff_customer_identity': ['customer_unique_id'],
    'hashdiff_customer_address': ['customer_zip_code_prefix', 'customer_city', 'customer_state']
} %}

{{ staging(
    source_name=source_name,
    source_table=source_table,
    source_date_col=source_date_col,
    business_key_cols=business_key_cols,
    hashdiff_satellite_dict=hashdiff_satellite_dict
)}}