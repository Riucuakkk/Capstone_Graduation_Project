{{ config(
    materialized = 'incremental',
    incremental_strategy = 'append',
    tags = ['source']
) }}

{% set source_name = 'source' %}
{% set source_table = 'order_payments' %}
{% set source_model = 'v_stg_source_order_payments' %}
{% set unique_key = 'order_payment_hashkey' %}
{% set source_business_key_cols = ['order_id', 'payment_sequential'] %}
{% set foreign_business_key_cols = {
    'order_hashkey': ['order_id']
} %}

{{ link(
    source_model = source_model,
    source_name = source_name,
    source_table = source_table,
    unique_key = unique_key,
    source_business_key_cols = source_business_key_cols,
    foreign_business_key_cols = foreign_business_key_cols
) }}
