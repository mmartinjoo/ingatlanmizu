{% macro city_name(col) -%}
case
    -- Budapest XIII. kerület, Angyalföld -> XIII. kerület
    when {{ col }} ilike '%Budapest%' then  
        btrim(split_part(regexp_replace({{ col }}, 'Budapest ', ''), ',', 1))

    -- Szombathely, Olad -> Szombathely
    else
        btrim(split_part({{ col }}, ',', 1))
end
{% endmacro %}

{% macro location_detail(col) -%}
nullif(btrim(split_part({{ col }}, ',', 2)), '')
{% endmacro %}