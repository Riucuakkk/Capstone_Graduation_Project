{{ config(
    materialized='view'
)}}

{% set source_name = 'source' %}
{% set source_table = 'order_items' %}
{% set source_date_col = 'shipping_limit_date' %}
{% set business_key_cols = ['order_id', 'order_item_id'] %}

{% set hashdiff_satellite_dict = {
    'hashdiff_order_item_details': ['order_item_id','product_id','seller_id','price','freight_value']
} %}

{{ staging(
    source_name=source_name,
    source_table=source_table,
    source_date_col=source_date_col,
    business_key_cols=business_key_cols,
    hashdiff_satellite_dict=hashdiff_satellite_dict
) }}