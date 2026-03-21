{{ config(
    materialized = 'incremental',
    incremental_strategy = 'merge',
    unique_key = ['review_hashkey', 'hashdiff'],
    skip_matched_step = true,
    auto_liquid_cluster = true,
    tags = ['source']
) }}

{% set source_name = 'source' %}
{% set source_table = 'order_reviews' %}
{% set hashdiff_col = 'hashdiff_review_details' %}
{% set hub_hashkey = 'review_hashkey' %}
{% set source_model = 'v_stg_source_order_reviews' %}
{% set list_cols = [
    'review_score',
    'review_comment_title',
    'review_comment_message',
    'review_creation_date',
    'review_answer_timestamp'
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