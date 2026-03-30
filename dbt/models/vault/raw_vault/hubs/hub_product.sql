{{ config(
    materialized = 'incremental',
    incremental_strategy = 'append',
    tags = ['source']
) }}

{% set source_name = 'source' %}
{% set unique_key = 'product_hashkey' %}
{% set business_key = 'product_id' %}
{% set source_table = 'products' %}
{% set source_model = 'v_stg_source_products' %}

{{ hub(
    source_model = source_model,
    source_name = source_name,
    source_table = source_table,
    unique_key = unique_key,
    business_key = business_key
) }}
