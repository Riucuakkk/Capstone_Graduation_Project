{{ config(
    materialized='view'
)}}

{% set source_name = 'source' %}
{% set source_table = 'payments' %}
{% set source_date_col = none %}
{% set business_key_cols = ['order_id', 'payment_sequential'] %}

{{ stage(
    source_name=source_name,
    source_table=source_table,
    source_date_col=source_date_col,
    business_key_cols=business_key_cols
) }}