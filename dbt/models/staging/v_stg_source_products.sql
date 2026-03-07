{{ config(
    materialized='view'
) }}

{% set source_name = 'source' %}
{% set source_table = 'products' %}
{% set source_date_col = none %}

{{ stage(
    source_name=source_name,
    source_table=source_table,
    source_date_col=source_date_col
) }}