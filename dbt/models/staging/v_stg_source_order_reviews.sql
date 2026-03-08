{{ config(
    materialized='view'
)}}

{% set source_name = 'source' %}
{% set source_table = 'order_reviews' %}
{% set source_date_col = 'review_creation_date' %}
{% set business_key_cols = ['review_id'] %}

{{ staging(
    source_name=source_name,
    source_table=source_table,
    source_date_col=source_date_col,
    business_key_cols=business_key_cols
) }}