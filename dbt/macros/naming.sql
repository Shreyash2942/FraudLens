{% macro fraudlens_relation_name(layer_name, dataset_name) -%}
    {%- set layer = layer_name | upper -%}
    {%- set dataset = dataset_name | upper -%}
    {{ return(layer ~ '_' ~ dataset) }}
{%- endmacro %}

{% macro fraudlens_source_name(dataset_name) -%}
    {{ return(source('bronze', dataset_name)) }}
{%- endmacro %}
