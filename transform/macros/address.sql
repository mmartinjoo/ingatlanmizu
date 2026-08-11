{% macro city_name(col) -%}
ltrim(rtrim(split_part({{ col }}, ',', 1)))
{% endmacro %}

{% macro location_detail(col) -%}
ltrim(rtrim(split_part({{ col }}, ',', 2)))
{% endmacro %}