{{ config(
    materialized='view'
)}}

{% set source_name = 'source' %}
{% set source_table = 'order_payments' %}
{% set source_date_col = none %}
{% set business_key_cols = ['order_id', 'payment_sequential'] %}

{% set hashdiff_satellite_dict = {
    'hashdiff_order_payment_details': ['payment_type', 'payment_installments', 'payment_value']
} %}

{{ staging( 
    source_name=source_name,
    source_table=source_table,
    source_date_col=source_date_col,
    business_key_cols=business_key_cols,
    hashdiff_satellite_dict=hashdiff_satellite_dict
) }}