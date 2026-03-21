{% macro satellite(raw_sql, table_hash_key, source_name) %}

WITH source_data AS (
    {{ raw_sql }}
),
target_data AS (
    SELECT *
    FROM (
        SELECT
            t.*,
            ROW_NUMBER() OVER (
                PARTITION BY {{ table_hash_key }}
                ORDER BY source_event_date DESC, load_timestamp DESC
            ) AS rn
        FROM {{ this }} t
        WHERE t.record_source LIKE '{{ source_name }}%'
    ) x
    WHERE rn = 1
),
insert_data AS (

    SELECT *
    FROM source_data s
    WHERE NOT EXISTS (
        SELECT 1
        FROM target_data t
        WHERE s.{{ table_hash_key }} = t.{{ table_hash_key }}
    )

    UNION ALL

    SELECT *
    FROM source_data s
    WHERE EXISTS (
        SELECT 1
        FROM target_data t
        WHERE s.{{ table_hash_key }} = t.{{ table_hash_key }}
          AND s.hashdiff <> t.hashdiff
    )
)

SELECT *
FROM insert_data

{% endmacro %}

{% macro sat(source_model, source_name, source_table, hub_hashkey, hashdiff_name, list_cols) %}

SELECT
    hashkey AS {{ hub_hashkey }},
    {{ hashdiff_name }} AS hashdiff,
    '{{ var("target_date") }}' AS source_event_date,
    CURRENT_TIMESTAMP AS load_timestamp,
    CONCAT('{{ source_name }}', '__', '{{ source_table }}') AS record_source
    {% for col in list_cols %},
    {{ col }}
    {% endfor %}
FROM {{ ref(source_model) }}
WHERE source_event_date = '{{ var("target_date") }}'

{% endmacro %}