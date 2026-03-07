{% macro stage(source_name, source_table, source_date_col = None, business_key_cols = None) %}

{%- set columns = get_columns(source(source_name, source_table)) -%}

SELECT

{{ hash_column(business_key_cols, source_name) }} as hashkey,

{% for col in columns %}
    src.{{ col }}{% if not loop.last %},{% endif %}
{% endfor %},

'{{ var("target_date") }}' as source_date,
current_timestamp as load_timestamp,
'{{ source_name }}' as source_system

FROM {{ source(source_name, source_table) }} src

{% if source_date_col is not none %}
WHERE {{ to_yyyymmdd_str('src.' ~ source_date_col) }} = '{{ var("target_date") }}'
{% endif %}

{% endmacro %}