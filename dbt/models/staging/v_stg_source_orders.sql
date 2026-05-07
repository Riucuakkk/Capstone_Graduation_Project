{{ config(
  materialized='view'
)}}

{% set source_name = 'source' %}
{% set source_table = 'orders' %}
{% set source_date_col = 'order_purchase_timestamp' %}
{% set business_key_cols = ['order_id'] %}

{% set hashdiff_satellite_dict = {
    'hashdiff_order_timestamps': ['order_purchase_timestamp', 'order_approved_at', 'order_delivered_carrier_date', 'order_delivered_customer_date', 'order_estimated_delivery_date'],
    'hashdiff_order_status': ['order_status']
} %}

{{ staging(source_name=source_name
        ,source_table=source_table
        ,source_date_col=source_date_col
        ,business_key_cols=business_key_cols
        ,hashdiff_satellite_dict=hashdiff_satellite_dict
        )
}}
