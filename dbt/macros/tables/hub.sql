{% macro hub(
    source_model = none, source_name = none, source_table = none, unique_key = none, business_key = none
) %}
    SELECT
        hashkey AS {{ unique_key }},
        {{ business_key }} AS business_key,
        '{{ var("target_date") }}' AS source_event_date,
        CONCAT('{{ source_name }}', '__', '{{ source_table }}') AS record_source,
        CURRENT_TIMESTAMP AS load_timestamp
    FROM {{ ref(source_model) }}
    WHERE source_event_date = '{{ var("target_date") }}'
{% endmacro %}