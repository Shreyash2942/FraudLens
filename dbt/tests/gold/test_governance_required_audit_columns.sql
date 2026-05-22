{{ config(tags=['quality', 'quality_critical', 'governance_critical', 'contract_critical', 'audit_critical', 'validation_critical']) }}

with violations as (
    select 'fact_transactions' as model_name, count(*) as violation_count
    from {{ ref('fact_transactions') }}
    where ingestion_batch_id is null
       or source_file_name is null
       or ingested_at_utc is null
       or created_at_utc is null
       or updated_at_utc is null
       or source_system is null
       or pipeline_run_id is null
       or pipeline_processed_at_utc is null
       or lineage_run_id is null

    union all

    select 'fact_fraud_alerts' as model_name, count(*) as violation_count
    from {{ ref('fact_fraud_alerts') }}
    where ingestion_batch_id is null
       or source_file_name is null
       or ingested_at_utc is null
       or created_at_utc is null
       or updated_at_utc is null
       or source_system is null
       or pipeline_run_id is null
       or pipeline_processed_at_utc is null
       or lineage_run_id is null

    union all

    select 'fact_payment_events' as model_name, count(*) as violation_count
    from {{ ref('fact_payment_events') }}
    where ingestion_batch_id is null
       or source_file_name is null
       or ingested_at_utc is null
       or created_at_utc is null
       or updated_at_utc is null
       or source_system is null
       or pipeline_run_id is null
       or pipeline_processed_at_utc is null
       or lineage_run_id is null

    union all

    select 'kpi_daily_fraud_operations' as model_name, count(*) as violation_count
    from {{ ref('kpi_daily_fraud_operations') }}
    where ingestion_batch_id is null
       or source_file_name is null
       or ingested_at_utc is null
       or created_at_utc is null
       or updated_at_utc is null
       or source_system is null
       or pipeline_run_id is null
       or pipeline_processed_at_utc is null
       or lineage_run_id is null

    union all

    select 'kpi_portfolio_risk_snapshot' as model_name, count(*) as violation_count
    from {{ ref('kpi_portfolio_risk_snapshot') }}
    where ingestion_batch_id is null
       or source_file_name is null
       or ingested_at_utc is null
       or created_at_utc is null
       or updated_at_utc is null
       or source_system is null
       or pipeline_run_id is null
       or pipeline_processed_at_utc is null
       or lineage_run_id is null
)
select *
from violations
where violation_count > 0
