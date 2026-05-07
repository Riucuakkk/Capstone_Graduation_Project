{% macro get_as_of_date() %}
    {{ return(var("as_of_date", run_started_at.strftime("%Y%m%d"))) }}
{% endmacro %}

{% macro use_as_of_date_filter() %}
    {{ return(var("use_as_of_date_filter", false)) }}
{% endmacro %}
