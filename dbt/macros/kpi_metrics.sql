{% macro fraudlens_safe_divide(numerator_expr, denominator_expr, default_value='0') -%}
    case
        when {{ denominator_expr }} is null or {{ denominator_expr }} = 0 then {{ default_value }}
        else {{ numerator_expr }} / {{ denominator_expr }}
    end
{%- endmacro %}

{% macro fraudlens_pct(numerator_expr, denominator_expr, scale=100, default_value='0') -%}
    ({{ fraudlens_safe_divide(numerator_expr, denominator_expr, default_value) }}) * {{ scale }}
{%- endmacro %}

{% macro fraudlens_bounded_pct(numerator_expr, denominator_expr, min_value=0, max_value=100) -%}
    greatest({{ min_value }}, least({{ max_value }}, {{ fraudlens_pct(numerator_expr, denominator_expr) }}))
{%- endmacro %}
