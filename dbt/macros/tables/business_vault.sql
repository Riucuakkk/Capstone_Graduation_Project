{% macro latest_by_key(model_name, partition_by, columns, order_by='source_event_date desc nulls last, load_timestamp desc') -%}
(
    select
        {{ partition_by }}
        {%- for col in columns %}
        , {{ col }}
        {%- endfor %}
    from (
        select
            {{ partition_by }}
            {%- for col in columns %}
            , {{ col }}
            {%- endfor %}
            ,
            row_number() over (
                partition by {{ partition_by }}
                order by {{ order_by }}
            ) as rn
        from {{ ref(model_name) }}
    ) t
    where rn = 1
)
{%- endmacro %}
