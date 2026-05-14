{% macro fraudlens_clean_text(expression, uppercase=false) -%}
    {%- if uppercase -%}
        nullif(upper(trim(cast({{ expression }} as string))), '')
    {%- else -%}
        nullif(trim(cast({{ expression }} as string)), '')
    {%- endif -%}
{%- endmacro %}

{% macro fraudlens_clean_boolean(expression) -%}
    case
        when {{ expression }} is null then null
        when upper(trim(cast({{ expression }} as string))) in ('TRUE', 'T', 'Y', 'YES', '1') then true
        when upper(trim(cast({{ expression }} as string))) in ('FALSE', 'F', 'N', 'NO', '0') then false
        else null
    end
{%- endmacro %}

{% macro fraudlens_clean_int(expression) -%}
    cast({{ expression }} as int)
{%- endmacro %}

{% macro fraudlens_clean_decimal(expression, precision=18, scale=2) -%}
    cast({{ expression }} as decimal({{ precision }}, {{ scale }}))
{%- endmacro %}

{% macro fraudlens_clean_date(expression) -%}
    cast({{ expression }} as date)
{%- endmacro %}

{% macro fraudlens_clean_timestamp(expression) -%}
    cast({{ expression }} as timestamp)
{%- endmacro %}
