{{ config(
    materialized = 'incremental',
    incremental_strategy = 'merge',
    unique_key = ['order_hashkey', 'hashdiff'],
    skip_matched_step = true,
    auto_liquid_cluster = true,
    tags = ['source']
) }}

{% set source_name = 'source' %}
{% set source_table = 'orders' %}
{% set hashdiff_col = 'hashdiff_order_timestamps' %}
{% set hub_hashkey = 'order_hashkey' %}
{% set source_model = 'v_stg_source_orders' %}
{% set list_cols = [
    'order_purchase_timestamp',
    'order_approved_at',
    'order_delivered_carrier_date',
    'order_delivered_customer_date',
    'order_estimated_delivery_date'
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