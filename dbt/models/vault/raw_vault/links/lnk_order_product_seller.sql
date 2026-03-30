{{ config(
    materialized = 'incremental',
    incremental_strategy = 'append',
    tags = ['source']
) }}

{% set source_name = 'source' %}
{% set source_table = 'order_items' %}
{% set source_model = 'v_stg_source_order_items' %}
{% set unique_key = 'order_product_seller_hashkey' %}
{% set source_business_key_cols = ['order_id', 'order_item_id', 'product_id', 'seller_id'] %}
{% set foreign_business_key_cols = {
    'order_hashkey': ['order_id'],
    'product_hashkey': ['product_id'],
    'seller_hashkey': ['seller_id']
} %}

{{ link(
    source_model = source_model,
    source_name = source_name,
    source_table = source_table,
    unique_key = unique_key,
    source_business_key_cols = source_business_key_cols,
    foreign_business_key_cols = foreign_business_key_cols
) }}
