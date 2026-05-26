{% macro fraudlens_required_audit_columns() -%}
    {{ return([
        'ingestion_batch_id',
        'source_file_name',
        'ingested_at_utc',
        'created_at_utc',
        'updated_at_utc',
        'source_system',
        'pipeline_run_id',
        'pipeline_processed_at_utc',
        'lineage_run_id'
    ]) }}
{%- endmacro %}

{% macro fraudlens_source_system_name() -%}
    {{ return(env_var('FRAUDLENS_SOURCE_SYSTEM', 'synthetic_generator')) }}
{%- endmacro %}

{% macro fraudlens_pipeline_run_id() -%}
    {{ return(invocation_id) }}
{%- endmacro %}

{% macro fraudlens_trace_audit_projection(ingestion_batch_expr, source_file_expr, ingested_at_expr, created_at_expr, updated_at_expr, pipeline_processed_at_expr, lineage_run_expr, source_system_expr=none, pipeline_run_id_expr=none) -%}
    {{ ingestion_batch_expr }} as ingestion_batch_id,
    {{ source_file_expr }} as source_file_name,
    {{ ingested_at_expr }} as ingested_at_utc,
    {{ created_at_expr }} as created_at_utc,
    {{ updated_at_expr }} as updated_at_utc,
    {% if source_system_expr is none -%}
    '{{ fraudlens_source_system_name() }}' as source_system,
    {% else -%}
    {{ source_system_expr }} as source_system,
    {% endif -%}
    {% if pipeline_run_id_expr is none -%}
    '{{ fraudlens_pipeline_run_id() }}' as pipeline_run_id,
    {% else -%}
    {{ pipeline_run_id_expr }} as pipeline_run_id,
    {% endif -%}
    {{ pipeline_processed_at_expr }} as pipeline_processed_at_utc,
    {{ lineage_run_expr }} as lineage_run_id
{%- endmacro %}

{% macro fraudlens_pipeline_audit_projection(alias_name='src') -%}
    {{ fraudlens_trace_audit_projection(
        alias_name ~ '.INGESTION_BATCH_ID',
        alias_name ~ '.SOURCE_FILE_NAME',
        alias_name ~ '.INGESTED_AT_UTC',
        alias_name ~ '.INGESTED_AT_UTC',
        'current_timestamp',
        'current_timestamp',
        "'" ~ invocation_id ~ "'"
    ) }}
{%- endmacro %}
