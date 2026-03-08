{{ config(
    materialized='view'
)}}

{% set source_name = 'source' %}
{% set source_table = 'order_items' %}
{% set source_date_col = 'shipping_limit_date' %}
{% set business_key_cols = ['order_id', 'order_item_id'] %}

{{ staging(
    source_name=source_name,
    source_table=source_table,
    source_date_col=source_date_col,
    business_key_cols=business_key_cols
) }}