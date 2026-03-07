{{ config(
    materialized='view'
) }}

{% set source_name = 'source' %}
{% set source_table = 'exchange_rate' %}
{% set source_date_col = 'date' %}
{% set business_key_cols = ['date', 'currency'] %}

SELECT
    {{ hash_column(business_key_cols, source_name) }} as hashkey,
    date,
    currency,
    rate,

    '{{ var("target_date") }}' as source_date,
    cast(current_timestamp as timestamp) as load_timestamp,
    '{{ source_name }}' as source_system

FROM {{ source(source_name, source_table) }}

{% if execute %}
WHERE {{ to_yyyymmdd_str(source_date_col) }} = '{{ var("target_date") }}'
{% endif %}