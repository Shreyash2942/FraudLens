{% macro fraudlens_required_audit_columns() -%}
    {{ return([
        'record_source',
        'source_record_id',
        'ingested_at',
        'effective_at',
        'created_at',
        'updated_at',
        'created_by',
        'updated_by',
        'change_reason_code',
        'lineage_run_id'
    ]) }}
{%- endmacro %}

{% macro fraudlens_pipeline_audit_projection(alias_name='src') -%}
    {{ alias_name }}.INGESTION_BATCH_ID as ingestion_batch_id,
    {{ alias_name }}.SOURCE_FILE_NAME as source_file_name,
    {{ alias_name }}.INGESTED_AT_UTC as ingested_at_utc,
    current_timestamp as pipeline_processed_at_utc,
    '{{ invocation_id }}' as lineage_run_id
{%- endmacro %}
