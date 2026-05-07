{{ config(
    materialized='view'
) }}

{% set source_name = 'source' %}
{% set source_table = 'exchange_rates' %}
{% set source_date_col = 'data_date' %}
{% set business_key_cols = ['data_date', 'currency'] %}

{{ staging(
    source_name=source_name,
    source_table=source_table,
    source_date_col=source_date_col,
    business_key_cols=business_key_cols
) }}
