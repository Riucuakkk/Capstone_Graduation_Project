{%- macro hash_column(columns_list, source_name) -%}
    {%- set hex_columns = [] -%}
    {%- set len = columns_list | length -%}
    {%- for column in columns_list -%}
        {%- if loop.index != len -%}
            {%- set column_string = "COALESCE(TRIM(CAST(" ~ column ~ " AS text)), '') || " -%}
        {%- else -%}
            {%- set column_string = "COALESCE(TRIM(CAST(" ~ column ~ " AS text)), '') " -%}
        {%- endif -%}
        {%- do hex_columns.append(column_string) -%}
    {%- endfor -%}

    {%- set str = "'" ~ source_name ~ "__' || " ~ hex_columns | join('') -%}
    md5({{ str }})
{%- endmacro -%}