{{ config(
    materialized = 'incremental',
    incremental_strategy = 'merge',
    unique_key = ['order_review_hashkey'],
    skip_matched_step = true,
    auto_liquid_cluster = true,
    tags = ['source']
) }}

{% set source_name = 'source' %}
{% set source_table = 'order_reviews' %}
{% set source_model = 'v_stg_source_order_reviews' %}
{% set unique_key = 'order_review_hashkey' %}
{% set source_business_key_cols = ['order_id', 'review_id'] %}
{% set foreign_business_key_cols = {
    'order_hashkey': ['order_id'],
    'review_hashkey': ['review_id']
} %}

{{ link(
    source_model = source_model,
    source_name = source_name,
    source_table = source_table,
    unique_key = unique_key,
    source_business_key_cols = source_business_key_cols,
    foreign_business_key_cols = foreign_business_key_cols
) }}