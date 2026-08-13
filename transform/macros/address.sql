{% macro city_name(col) -%}
btrim(split_part({{ col }}, ',', 1))
{% endmacro %}

{% macro location_detail(col) -%}
nullif(btrim(split_part({{ col }}, ',', 2)), '')
{% endmacro %}