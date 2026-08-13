{% macro hu_numeric(col) -%}
-- Converts human-readable numeric values to a number
-- "49,9 millió Ft" -> 49.9 
-- "65 m²" -> 65
-- Non-breaking spaces (chr(160)) are replaced to spaces
-- It returns NULL if the result is empty
nullif(
    replace(
        regexp_replace(
            replace({{ col }}, chr(160), ' '), 
            '[^0-9,]', '', 'g'
        ), ',', '.'
    ), ''
)::numeric
{%- endmacro %}

{% macro price_magnitude(col) -%}
-- Returns the magnitude of a human-readable price
-- "49,9 millió Ft" -> 1000000
case
    when {{ col }} ilike '%milliárd%'  then 1000000000
    when {{ col }} ilike '%millió%'    then 1000000
    when {{ col }} ilike '%ezer%'      then 1000
    else 1
end
{%- endmacro %}