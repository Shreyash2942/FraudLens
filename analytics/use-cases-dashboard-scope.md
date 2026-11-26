# Analytics use cases and dashboard scope

Issue [#93](https://github.com/Shreyash2942/FraudLens/issues/93), parent [#92](https://github.com/Shreyash2942/FraudLens/issues/92), Phase 9: Analytics & Dashboard. Design date: November 25, 2026 (America/New_York).

## Audiences and decisions

| Audience | Decisions to support | Planned dashboard | Expected use |
| --- | --- | --- | --- |
| Executive / fraud strategy sponsor | Recognize changes in transaction and alert activity; direct attention to high-severity exposure and portfolio risk posture. | Executive KPI (#95) | Read-only daily trend review and portfolio demo; distinguish daily activity from a build-wide snapshot. |
| Fraud operations lead | Understand alert severity/status/queue and owning-team distribution; prioritize investigation of operational patterns. | Fraud Operations (#96) | Read-only operational review and alert-to-case context; not an action queue or case-management application. |
| Fraud / payments analyst | Compare channel and transaction-status mix, reversal/cross-border patterns and supporting payment context. | Transaction & Channel Analysis (#97) | Filtered exploration and governed identifier drill-through; reconcile observations to Gold rows. |

All audiences consume the same governed Gold definitions. These are proposed portfolio personas, not claims of stakeholder interviews or production user acceptance. Named operational owners and acceptance evidence are established during dashboard review.

Each page must explain its audience, date meaning, grain, active filters, source/build provenance and limitations. A visibly synthetic-data label is mandatory. Use masked/minimal identifiers in demo exports; never expose service credentials or banking-like detail merely because a source field exists.

## Priority reporting questions

P0 is the first dashboard slice after BI/data access and grain validation. P1 is conditional: it must not be shown as a completed feature simply because a model column exists. Counts and sums over validated additive grain are allowed presentation aggregations; fraud classifications, KPI ratios, currency conversion and cohort rules belong in governed Gold/dbt logic.

| ID / priority | Business question | Audience / page | Source-defined outputs and acceptance |
| --- | --- | --- | --- |
| Q01 / P0 | How do daily transaction and alert volumes change? | Executive | Daily `total_transactions` and `total_fraud_alerts`; display distinct transaction-date and alert-created-date activity meanings. Missing calendar observations are not automatically healthy zero-volume days. |
| Q02 / P0 | How does alert activity compare with transaction activity by day? | Executive | Canonical daily `alert_rate_pct`. Label as an alert-to-transaction activity ratio, not confirmed fraud incidence, detection accuracy or a matched cohort conversion rate. Multiple alerts can make this ratio exceed 100%; never clamp it in BI. |
| Q03 / P0 | What fraction of daily alerts is high severity or linked to cases? | Executive / Fraud Operations | Canonical daily `high_severity_alert_rate_pct`, `fraud_case_open_rate_pct` and their available counts; validate alert/case uniqueness before trusting totals. |
| Q04 / P0 | Which severity, status, queues and owning teams contain alert activity? | Fraud Operations | Gold alert rows with `alert_severity`, `alert_status`, `queue_code`, owning team/business unit and case context. Use Gold status values and validated alert grain; a current status distribution is not a historical backlog trend. |
| Q05 / P1 | What does the existing SLA flag say about case opening? | Fraud Operations | `is_sla_breached` describes case opening after the due time; it is null without the required case/open timestamps. Label that scope and show missing coverage; do not present it as a live overdue-open-alert or resolution-SLA measure. |
| Q06 / P0 | How do transaction status, reversal and cross-border mix vary? | Analyst | Gold transaction status and `is_reversal`/`is_cross_border` flags; compare counts. Existing daily `reversal_rate_pct` is global/day only; new period or dimensional ratios require governed Gold support. |
| Q07 / P0 | Which channels and rails account for transaction activity? | Analyst | Transaction-grain counts, Gold channel-event lookup and `payment_rail_code`; validate lookup uniqueness and unknown-channel handling before cross-filtering. |
| Q08 / P1 | What is the current build-wide high-risk-event and open alert/case posture? | Executive | Existing portfolio snapshot rates/counts, clearly labeled whole-build coverage. Not an event-date-filtered KPI or a historical time series; validate cross-model coverage before comparison. |
| Q09 / P1, currency gate | What financial loss/recovery or transaction amount can be reported safely? | Executive / Analyst | Amounts only with demonstrated currency/coverage semantics. Transaction amounts must stay grouped by their own currency; current global loss/recovery aggregates and recovery rates are blocked until a single-currency or governed currency-aware contract is proven. |

Every implemented visual must retain its question ID, model/field lineage, declared grain and comparison/reconciliation evidence. No invented target, alert threshold, financial materiality limit or benchmark is implied by these questions. Business targets remain an explicit future owner decision.
