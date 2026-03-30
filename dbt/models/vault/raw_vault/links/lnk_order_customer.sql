{{ config(
    materialized = 'incremental',
    incremental_strategy = 'append',
    tags = ['source']
) }}

{% set source_name = 'source' %}
{% set source_table = 'orders' %}
{% set source_model = 'v_stg_source_orders' %}
{% set unique_key = 'order_customer_hashkey' %}
{% set source_business_key_cols = ['order_id', 'customer_id'] %}
{% set foreign_business_key_cols = {
    'order_hashkey': ['order_id'],
    'customer_hashkey': ['customer_id']
} %}

{{ link(
    source_model = source_model,
    source_name = source_name,
    source_table = source_table,
    unique_key = unique_key,
    source_business_key_cols = source_business_key_cols,
    foreign_business_key_cols = foreign_business_key_cols
) }}
