{% macro number_of_rooms(col) -%}
coalesce(substring({{ col }} from '(^\d+)')::numeric, 0)
    + (coalesce(substring({{ col }} from '\+\s*(\d+)')::numeric, 0) * 0.5)
{% endmacro %}