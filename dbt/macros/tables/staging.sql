{% macro staging(
    source_name,
    source_table,
    business_key_cols,
    hashdiff_satellite_dict = none,
    source_date_col = none
) %}

{%- set src = source(source_name, source_table) -%}
{%- set columns = adapter.get_columns_in_relation(src) -%}
{%- set as_of_date = get_as_of_date() -%}
{%- set apply_as_of_date_filter = use_as_of_date_filter() -%}
{%- if source_date_col is not none and apply_as_of_date_filter -%}
{%- set source_event_date_expr = to_yyyymmdd_str('src."' ~ source_date_col ~ '"') -%}
{%- set fallback_as_of_date_sql -%}
(
    SELECT max({{ to_yyyymmdd_str('src_fallback."' ~ source_date_col ~ '"') }})
    FROM {{ src }} as src_fallback
    WHERE src_fallback."{{ source_date_col }}" IS NOT NULL
      AND {{ to_yyyymmdd_str('src_fallback."' ~ source_date_col ~ '"') }} <= '{{ as_of_date }}'
)
{%- endset -%}
{%- endif -%}

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
    {{ hash_column(columns | map(attribute='column') | list, source_name) }} as hashdiff_full

    -- HASHDIFF PER SAT
    {% if hashdiff_satellite_dict is not none %}
    {% for k, v in hashdiff_satellite_dict.items() %}
    , {{ hash_column(v, source_name) }} as {{ k }}
    {% endfor %}
    {% endif %}

    -- META COLUMNS
    ,
    {% if source_date_col is not none %}
    {{ to_yyyymmdd_str('src."' ~ source_date_col ~ '"') }} as source_event_date,
    {% else %}
    '{{ as_of_date }}' as source_event_date,
    {% endif %}
    current_timestamp as load_timestamp,
    '{{ source_name }}' as record_source

FROM {{ src }} as src

WHERE 1=1

-- FILTER BUSINESS KEY NOT NULL
{% for col in business_key_cols %}
AND src."{{ col }}" IS NOT NULL
{% endfor %}

-- FILTER BATCH DATE FOR INCREMENTAL LOADS
{% if source_date_col is not none and apply_as_of_date_filter %}
AND {{ source_event_date_expr }} = coalesce({{ fallback_as_of_date_sql }}, '{{ as_of_date }}')
{% endif %}

{% endmacro %}
