{{ config(
  materialized='view'
)}}

{% set source_name = 'source' %}
{% set source_table = 'orders' %}
{% set source_date_col = 'order_purchase_timestamp' %}
{% set business_key_cols = ['order_id'] %}

{{ stage(source_name=source_name
        ,source_table=source_table
        ,source_date_col=source_date_col
        ,business_key_cols=business_key_cols
        )
}}
