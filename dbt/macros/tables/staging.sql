{% macro staging(
    source_name,
    source_table,
    business_key_cols,
    hashdiff_satellite_dict = none,
    source_date_col = none
) %}

{%- set src = source(source_name, source_table) -%}
{%- set columns = adapter.get_columns_in_relation(src) -%}

SELECT
    -- HASHKEY
    {{ hash_column(business_key_cols, source_name) }} as hashkey,

    -- CLEANED COLUMNS
    {% for col in columns %}
        {% if col.data_type | lower in ['varchar','text','character varying','char'] %}
        case
            when lower(trim(src."{{ col.column }}")) in ('', 'null', 'none', 'n/a')
            then null
            else trim(src."{{ col.column }}")
        end as "{{ col.column }}"
        {% else %}
        src."{{ col.column }}"
        {% endif %}
        {% if not loop.last %},{% endif %}
    {% endfor %},

    -- HASHDIFF FULL
    {{ hash_column(columns | map(attribute='column') | list, source_name) }} as hashdiff_full,

    -- HASHDIFF PER SAT
    {% if hashdiff_satellite_dict is not none %}
    {% for k, v in hashdiff_satellite_dict.items() %}
    , {{ hash_column(v, source_name) }} as {{ k }}
    {% endfor %}
    {% endif %},

    -- META COLUMNS
    '{{ var("target_date") }}' as source_event_date,
    current_timestamp as load_timestamp,
    '{{ source_name }}' as record_source

FROM {{ src }} as src

WHERE 1=1

-- FILTER BUSINESS KEY NOT NULL
{% for col in business_key_cols %}
AND src."{{ col }}" IS NOT NULL
{% endfor %}

-- FILTER DATE
{% if source_date_col is not none %}
AND to_yyyymmdd_str(src."{{ source_date_col }}") = '{{ var("target_date") }}'
{% endif %}

{% endmacro %}