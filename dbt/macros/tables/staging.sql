{% macro staging(source_name, source_table, source_date_col = None, business_key_cols = None) %}

{%- set src = source(source_name, source_table) -%}
{%- set columns = adapter.get_columns_in_relation(src) -%}

SELECT
    {{ hash_column(business_key_cols, source_name) }} as hashkey,
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
    '{{ var("target_date") }}' as source_date,
    current_timestamp as load_timestamp,
    '{{ source_name }}' as source_system
FROM {{ src }} as src

{% if source_date_col is not none %}
WHERE TO_CHAR(src."{{ source_date_col }}", 'YYYYMMDD') = '{{ var("target_date") }}'
{% endif %}

{% endmacro %}