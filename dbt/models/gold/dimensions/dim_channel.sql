{{ config(alias='gold_dim_channel', tags=['gold', 'dim']) }}

select
    {{ fraudlens_fact_sk(['ce.channel_event_id']) }} as dim_channel_sk,
    ce.channel_event_id,
    ce.channel_code,
    ce.session_id,
    ce.branch_id,
    bl.branch_code,
    bl.branch_name,
    ce.event_country_code,
    ce.ip_country_code,
    ce.authentication_result_code,
    ce.session_risk_code,
    ce.ingestion_batch_id,
    ce.source_file_name,
    ce.ingested_at_utc,
    ce.pipeline_processed_at_utc,
    ce.lineage_run_id
from {{ ref('slv__channel_event') }} as ce
left join {{ ref('slv__branch_location') }} as bl
    on ce.branch_id = bl.branch_id
