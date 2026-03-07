{%- macro date_to_str(col) -%}
  case
    -- If already yyyymmdd string (length 8, all digits)
    when length(cast({{ col }} as varchar(100))) = 8 and regexp_like(cast({{ col }} as varchar(100)), '^[0-9]{8}$') then cast({{ col }} as varchar(100))
    -- If string in yyyy-mm-dd format, parse and format
    when length(cast({{ col }} as varchar(100))) = 10 and regexp_like(cast({{ col }} as varchar(100)), '^[0-9]{4}-[0-9]{2}-[0-9]{2}$') then date_format(cast({{ col }} as date), 'yyyyMMdd')
    -- If date or timestamp, format directly
    when try_cast({{ col }} as date) is not null then date_format(cast({{ col }} as date), 'yyyyMMdd')
    when try_cast({{ col }} as timestamp) is not null then date_format(cast({{ col }} as timestamp), 'yyyyMMdd')
    -- Try to parse any other string as date
    else date_format(try_cast({{ col }} as date), 'yyyyMMdd')
  end
{%- endmacro -%}

{% macro to_yyyymmdd_str(col) %}
    CASE
        WHEN {{ col }} IS NULL THEN NULL

        -- Timestamp / Date types

        WHEN typeof({{ col }}) IN ('date', 'timestamp', 'timestamp with time zone') THEN

            date_format(cast({{ col }} as date), 'yyyyMMdd')
 
        -- String already yyyymmdd

        WHEN regexp_like({{ col }}, '^[0-9]{8}$') THEN

            date_format(to_date({{ col }},'yyyyMMdd'), 'yyyyMMdd')
 
        -- yyyy-mm-dd

        WHEN regexp_like({{ col }}, '^[0-9]{4}-[0-9]{2}-[0-9]{2}$') THEN

            regexp_replace({{ col }}, '-', '')
 
        -- yyyy/mm/dd

        WHEN regexp_like(cast({{ col }} as string),
            '^[0-9]{1,2}/[0-9]{1,2}/[0-9]{4}$')
        THEN date_format(
            cast(try_to_timestamp({{ col }}, 'M/d/yyyy') as date),
            'yyyyMMdd'
        )

        WHEN regexp_like({{ col }}, '^[0-9]{4}/[0-9]{2}/[0-9]{2}$') THEN

            regexp_replace({{ col }}, '/', '')

        WHEN regexp_like(cast({{ col }} as string),
                '^[0-9]{1,2}/[0-9]{1,2}/[0-9]{4} [0-9]{1,2}:[0-9]{2}$')
            THEN date_format(
                cast(try_to_timestamp(cast({{ col }} as string), 'M/d/yyyy H:mm') as date),
                'yyyyMMdd'
            )
            
        WHEN regexp_like({{ col }}, '(AM|PM)') THEN

            date_format(
  coalesce(try_to_timestamp({{ col }}, 'M/d/yyyy HH:mm:ss a'), try_to_timestamp({{ col }}, 'M/d/yyyy H:mm:ss a'),try_to_timestamp({{ col }}, 'M/d/yyyy h:mm:ss a'))
  , 'yyyyMMdd') 

        ELSE

            date_format(

                cast(

                    try_cast({{ col }} as date)

                    as date

                ),

                'yyyyMMdd'

            )

    END
{% endmacro %}