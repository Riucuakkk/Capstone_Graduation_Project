{{ config(
    materialized='view'
)}}

{% set source_name = 'source' %}
{% set source_table = 'order_reviews' %}
{% set source_date_col = 'review_creation_date' %}
{% set business_key_cols = ['review_id'] %}

{% set hashdiff_satellite_dict = {
    'hashdiff_review_details': ['review_score', 'review_comment_title', 'review_comment_message', 'review_creation_date', 'review_answer_timestamp']
} %}

{{ staging(
    source_name=source_name,
    source_table=source_table,
    source_date_col=source_date_col,
    business_key_cols=business_key_cols,
    hashdiff_satellite_dict=hashdiff_satellite_dict
) }}