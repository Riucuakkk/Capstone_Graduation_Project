{{ config(
    materialized = 'incremental',
    incremental_strategy = 'merge',
    unique_key = ['order_hashkey'],
    skip_matched_step = true,
    auto_liquid_cluster = true,
    tags = ['source']
) }}

{% set source_name = 'source' %}
{% set unique_key = 'order_hashkey' %}
{% set business_key = 'order_id' %}
{% set source_table = 'orders' %}
{% set source_model = 'v_stg_source_orders' %}

{{ hub(
    source_model = source_model,
    source_name = source_name,
    source_table = source_table,
    unique_key = unique_key,
    business_key = business_key
) }}