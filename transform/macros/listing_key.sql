{% macro listing_key(source_name, col) -%}
concat('{{ source_name }}', ':', {{ col }})
{%- endmacro %}