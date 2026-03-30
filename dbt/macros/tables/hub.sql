{% macro hub(
    source_model = none, source_name = none, source_table = none, unique_key = none, business_key = none
) %}
    WITH source_data AS (
        SELECT
            hashkey AS {{ unique_key }},
            {{ business_key }} AS business_key,
            source_event_date AS source_event_date,
            CONCAT('{{ source_name }}', '__', '{{ source_table }}') AS record_source,
            CURRENT_TIMESTAMP AS load_timestamp
        FROM {{ ref(source_model) }}
    )

    SELECT s.*
    FROM source_data s
    {% if is_incremental() %}
    WHERE NOT EXISTS (
        SELECT 1
        FROM {{ this }} t
        WHERE t.{{ unique_key }} = s.{{ unique_key }}
    )
    {% endif %}
{% endmacro %}
