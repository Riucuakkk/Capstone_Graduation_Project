{{ config(
    materialized = 'incremental',
    incremental_strategy = 'merge',
    unique_key = ['customer_hashkey', 'hashdiff'],
    skip_matched_step = true,
    auto_liquid_cluster = true,
    tags = ['source']
) }}

{% set source_name = 'source' %}
{% set source_table = 'customers' %}
{% set hashdiff_col = 'hashdiff_customer_address' %}
{% set hub_hashkey = 'customer_hashkey' %}
{% set source_model = 'v_stg_source_customers' %}
{% set list_cols = ['customer_zip_code_prefix','customer_city','customer_state'] %}

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