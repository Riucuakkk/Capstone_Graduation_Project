{{ config(
    materialized = 'incremental',
    incremental_strategy = 'merge',
    unique_key = ['seller_hashkey'],
    skip_matched_step = true,
    auto_liquid_cluster = true,
    tags = ['source']
) }}

{% set source_name = 'source' %}
{% set unique_key = 'seller_hashkey' %}
{% set business_key = 'seller_id' %}
{% set source_table = 'sellers' %}
{% set source_model = 'v_stg_source_sellers' %}

{{ hub(
    source_model = source_model,
    source_name = source_name,
    source_table = source_table,
    unique_key = unique_key,
    business_key = business_key
) }}