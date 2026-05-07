{{ config(
    materialized = 'incremental',
    incremental_strategy = 'merge',
    unique_key = ['seller_hashkey', 'hashdiff'],
    tags = ['source']
) }}

{% set source_name = 'source' %}
{% set source_table = 'sellers' %}
{% set hashdiff_col = 'hashdiff_seller_address' %}
{% set hub_hashkey = 'seller_hashkey' %}
{% set source_model = 'v_stg_source_sellers' %}
{% set list_cols = [
    'seller_zip_code_prefix',
    'seller_city',
    'seller_state'
] %}
{% set raw_sql %}
    {{ sat(
        source_model=source_model,
        source_name=source_name,
        source_table=source_table,
        hub_hashkey=hub_hashkey,
        hashdiff_name=hashdiff_col,
        list_cols=list_cols
    ) }}
{% endset %}

{% if not is_incremental() %}
    {{ raw_sql }}
{% else %}
    {{ satellite(raw_sql, hub_hashkey, source_name ~ '__' ~ source_table) }}
{% endif %}
