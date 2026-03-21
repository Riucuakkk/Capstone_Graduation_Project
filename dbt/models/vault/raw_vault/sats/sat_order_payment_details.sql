{{ config(
    materialized = 'incremental',
    incremental_strategy = 'merge',
    unique_key = ['product_hashkey', 'hashdiff'],
    skip_matched_step = true,
    auto_liquid_cluster = true,
    tags = ['source']
) }}

{% set source_name = 'source' %}
{% set source_table = 'order_payments' %}
{% set hashdiff_col = 'hashdiff_order_payment_details' %}
{% set hub_hashkey = 'order_payment_hashkey' %}
{% set source_model = 'v_stg_source_order_payments' %}
{% set list_cols = [
    'payment_type',
    'payment_installments',
    'payment_value'
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