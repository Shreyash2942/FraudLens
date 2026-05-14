{{ config(alias='SILVER_FRAUD_ALERT', tags=['silver', 'conformed']) }}

select
    {{ fraudlens_clean_text('src.fraud_alert_id') }} as fraud_alert_id,
    {{ fraudlens_clean_text('src.risk_signal_id') }} as risk_signal_id,
    {{ fraudlens_clean_text('src.alert_status', uppercase=true) }} as alert_status,
    {{ fraudlens_clean_text('src.alert_severity', uppercase=true) }} as alert_severity,
    {{ fraudlens_clean_text('src.queue_code', uppercase=true) }} as queue_code,
    {{ fraudlens_clean_timestamp('src.created_at') }} as created_at,
    {{ fraudlens_clean_text('src.alert_type_code', uppercase=true) }} as alert_type_code,
    {{ fraudlens_clean_text('src.alert_source_code', uppercase=true) }} as alert_source_code,
    {{ fraudlens_clean_text('src.owning_business_unit_id') }} as owning_business_unit_id,
    {{ fraudlens_clean_text('src.owning_analyst_team_id') }} as owning_analyst_team_id,
    {{ fraudlens_clean_timestamp('src.service_level_due_at') }} as service_level_due_at,
    {{ fraudlens_clean_text('src.ingestion_batch_id') }} as ingestion_batch_id,
    {{ fraudlens_clean_text('src.source_file_name') }} as source_file_name,
    {{ fraudlens_clean_timestamp('src.ingested_at_utc') }} as ingested_at_utc,
    {{ fraudlens_clean_timestamp('src.pipeline_processed_at_utc') }} as pipeline_processed_at_utc,
    {{ fraudlens_clean_text('src.lineage_run_id') }} as lineage_run_id
from {{ ref('stg_bronze__fraud_alert') }} as src
{{ fraudlens_batch_where('src') }}
