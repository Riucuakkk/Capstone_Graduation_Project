{% macro link(
    source_model = none, source_name = none, source_table = none, unique_key = none, source_business_key_cols = none, foreign_business_key_cols = none
) %}

SELECT DISTINCT
    {{ hash_column(source_business_key_cols, source_name) }} AS {{ unique_key }},
    {% for name_hashkey, cols in foreign_business_key_cols.items() %}
        {{ hash_column(cols, source_name) }} AS {{ name_hashkey }}{% if not loop.last %},{% endif %}
    {% endfor %},
    '{{ var("target_date") }}' AS source_event_date,
    CONCAT('{{ source_name }}', '__', '{{ source_table }}') AS record_source,
    CURRENT_TIMESTAMP AS load_timestamp
FROM {{ ref(source_model) }}
WHERE source_event_date = '{{ var("target_date") }}'
{% for col in source_business_key_cols %}
    AND {{ col }} IS NOT NULL
{% endfor %}
{% for name_hashkey, cols in foreign_business_key_cols.items() %}
    {% for col in cols %}
    AND {{ col }} IS NOT NULL
    {% endfor %}
{% endfor %}

{% endmacro %}