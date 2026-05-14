{{ config(alias='SILVER_DECISION_RECORD', tags=['silver', 'conformed']) }}

select
    {{ fraudlens_clean_text('src.decision_id') }} as decision_id,
    {{ fraudlens_clean_text('src.fraud_case_id') }} as fraud_case_id,
    {{ fraudlens_clean_text('src.decision_type', uppercase=true) }} as decision_type,
    {{ fraudlens_clean_text('src.decision_status', uppercase=true) }} as decision_status,
    {{ fraudlens_clean_text('src.decision_maker_party_id') }} as decision_maker_party_id,
    {{ fraudlens_clean_timestamp('src.decided_at') }} as decided_at,
    {{ fraudlens_clean_text('src.decision_reason_code', uppercase=true) }} as decision_reason_code,
    {{ fraudlens_clean_text('src.decision_channel_code', uppercase=true) }} as decision_channel_code,
    {{ fraudlens_clean_text('src.policy_name') }} as policy_name,
    {{ fraudlens_clean_text('src.rule_set_version') }} as rule_set_version,
    {{ fraudlens_clean_text('src.ingestion_batch_id') }} as ingestion_batch_id,
    {{ fraudlens_clean_text('src.source_file_name') }} as source_file_name,
    {{ fraudlens_clean_timestamp('src.ingested_at_utc') }} as ingested_at_utc,
    {{ fraudlens_clean_timestamp('src.pipeline_processed_at_utc') }} as pipeline_processed_at_utc,
    {{ fraudlens_clean_text('src.lineage_run_id') }} as lineage_run_id
from {{ ref('stg_bronze__decision_record') }} as src
{{ fraudlens_batch_where('src') }}
