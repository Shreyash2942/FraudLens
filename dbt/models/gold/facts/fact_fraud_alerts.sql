{{ config(alias='GOLD_FACT_FRAUD_ALERTS', tags=['gold', 'fact'], materialized='incremental') }}

with fraud_alerts as (
    select *
    from {{ ref('slv__fraud_alert') }}
    {% if is_incremental() and var('fraudlens_batch_id', '') | length > 0 %}
    where ingestion_batch_id = '{{ var("fraudlens_batch_id") }}'
    {% endif %}
),
risk_signals as (
    select *
    from {{ ref('slv__risk_signal') }}
),
payment_instructions as (
    select *
    from {{ ref('slv__payment_instruction') }}
),
fraud_cases as (
    select *
    from {{ ref('slv__fraud_case') }}
),
decision_rollup as (
    select
        dr.fraud_case_id,
        count(dr.decision_id) as decision_count,
        max(dr.decided_at) as latest_decided_at
    from {{ ref('slv__decision_record') }} as dr
    group by dr.fraud_case_id
),
disposition_rollup as (
    select
        dr.fraud_case_id,
        count(cd.disposition_id) as disposition_count,
        sum(coalesce(cd.financial_impact_amount, 0)) as total_financial_impact_amount,
        sum(coalesce(cd.loss_amount, 0)) as total_loss_amount,
        sum(coalesce(cd.recovered_amount, 0)) as total_recovered_amount,
        sum(coalesce(cd.write_off_amount, 0)) as total_write_off_amount
    from {{ ref('slv__decision_record') }} as dr
    left join {{ ref('slv__case_disposition') }} as cd
        on dr.decision_id = cd.decision_id
    group by dr.fraud_case_id
)
select
    {{ fraudlens_fact_sk(['fa.fraud_alert_id', 'rs.risk_signal_id']) }} as fact_fraud_alert_sk,
    fa.fraud_alert_id,
    rs.risk_signal_id,
    rs.payment_instruction_id,
    coalesce(to_date(fa.created_at), to_date(rs.event_at), to_date(pi.event_at), pi.booking_date) as alert_created_date,
    fa.created_at as alert_created_at,
    rs.event_at as risk_event_at,
    pi.event_at as payment_event_at,
    pi.booking_date,
    fa.alert_status,
    fa.alert_severity,
    fa.alert_type_code,
    fa.alert_source_code,
    fa.queue_code,
    fa.owning_business_unit_id,
    fa.owning_analyst_team_id,
    fa.service_level_due_at,
    case
        when fa.alert_severity in ('HIGH', 'CRITICAL') then true
        else false
    end as is_high_severity_alert,
    rs.signal_type_code,
    rs.signal_score_amount,
    rs.risk_level,
    fc.fraud_case_id,
    fc.case_status,
    fc.case_priority_code,
    fc.case_type_code,
    fc.opened_at as case_opened_at,
    fc.closed_at as case_closed_at,
    case
        when fc.opened_at is not null and fa.created_at is not null then cast((unix_timestamp(fc.opened_at) - unix_timestamp(fa.created_at)) / 60 as int)
        else null
    end as minutes_to_case_open,
    case
        when fa.service_level_due_at is not null and fc.opened_at is not null and fc.opened_at > fa.service_level_due_at then true
        when fa.service_level_due_at is not null and fc.opened_at is not null then false
        else null
    end as is_sla_breached,
    coalesce(dr.decision_count, 0) as decision_count,
    dr.latest_decided_at,
    coalesce(disp.disposition_count, 0) as disposition_count,
    coalesce(disp.total_financial_impact_amount, 0) as total_financial_impact_amount,
    coalesce(disp.total_loss_amount, 0) as total_loss_amount,
    coalesce(disp.total_recovered_amount, 0) as total_recovered_amount,
    coalesce(disp.total_write_off_amount, 0) as total_write_off_amount,
    coalesce(fa.ingestion_batch_id, rs.ingestion_batch_id, pi.ingestion_batch_id, fc.ingestion_batch_id) as ingestion_batch_id,
    coalesce(fa.source_file_name, rs.source_file_name, pi.source_file_name, fc.source_file_name) as source_file_name,
    coalesce(fa.ingested_at_utc, rs.ingested_at_utc, pi.ingested_at_utc, fc.ingested_at_utc) as ingested_at_utc,
    coalesce(fa.pipeline_processed_at_utc, rs.pipeline_processed_at_utc, pi.pipeline_processed_at_utc, fc.pipeline_processed_at_utc) as pipeline_processed_at_utc,
    coalesce(fa.lineage_run_id, rs.lineage_run_id, pi.lineage_run_id, fc.lineage_run_id) as lineage_run_id
from fraud_alerts as fa
left join risk_signals as rs
    on fa.risk_signal_id = rs.risk_signal_id
left join payment_instructions as pi
    on rs.payment_instruction_id = pi.payment_instruction_id
left join fraud_cases as fc
    on fa.fraud_alert_id = fc.primary_alert_id
left join decision_rollup as dr
    on fc.fraud_case_id = dr.fraud_case_id
left join disposition_rollup as disp
    on fc.fraud_case_id = disp.fraud_case_id
