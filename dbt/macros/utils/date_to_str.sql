{%- macro date_to_str(col) -%}
  case
    when length(cast({{ col }} as varchar)) = 8 and cast({{ col }} as varchar) ~ '^[0-9]{8}$' 
      then cast({{ col }} as varchar)

    when length(cast({{ col }} as varchar)) = 10 and cast({{ col }} as varchar) ~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}$' 
      then to_char(cast({{ col }} as date), 'YYYYMMDD')

    when cast({{ col }} as varchar) ~ '^[0-9]{4}[-/][0-9]{2}[-/][0-9]{2}' 
      then to_char(cast({{ col }} as date), 'YYYYMMDD')

    when pg_typeof({{ col }})::text like 'timestamp%' or pg_typeof({{ col }})::text = 'date'
      then to_char(cast({{ col }} as date), 'YYYYMMDD')
    else to_char(cast({{ col }} as date), 'YYYYMMDD')
  end
{%- endmacro -%}

{% macro to_yyyymmdd_str(col) %}
    CASE
        WHEN {{ col }} IS NULL THEN NULL

        WHEN pg_typeof({{ col }})::text IN ('date', 'timestamp', 'timestamp without time zone', 'timestamp with time zone') 
            THEN to_char({{ col }}, 'YYYYMMDD')

        WHEN {{ col }}::text ~ '^[0-9]{8}$' 
            THEN {{ col }}::text

        WHEN {{ col }}::text ~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}$' 
            THEN regexp_replace({{ col }}::text, '-', '', 'g')
            
        WHEN {{ col }}::text ~ '^[0-9]{4}/[0-9]{2}/[0-9]{2}$' 
            THEN regexp_replace({{ col }}::text, '/', '', 'g')

        WHEN {{ col }}::text ~ '^[0-9]{1,2}/[0-9]{1,2}/[0-9]{4}'
            THEN to_char(to_date({{ col }}::text, 'MM/DD/YYYY'), 'YYYYMMDD')

        ELSE 
            CASE 
                WHEN {{ col }}::text ~ '^[0-9]{4}' THEN to_char({{ col }}::date, 'YYYYMMDD')
                ELSE NULL 
            END
    END
{% endmacro %}