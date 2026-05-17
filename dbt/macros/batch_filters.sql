{% macro fraudlens_batch_where(alias_name='src', column_name='INGESTION_BATCH_ID') -%}
    {%- if var('fraudlens_batch_id', '') | length > 0 -%}
        where {{ alias_name }}.{{ column_name }} = '{{ var("fraudlens_batch_id") }}'
    {%- endif -%}
{%- endmacro %}
