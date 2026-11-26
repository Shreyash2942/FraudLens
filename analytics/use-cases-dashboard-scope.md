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
| Q02 / P0, definition gate | How does alert activity compare with transaction activity by day? | Executive | Daily `alert_rate_pct` divides alert count by transaction count. Proposed label: alert-to-transaction activity ratio, not confirmed fraud incidence or a matched-cohort conversion. SQL is uncapped and multiple alerts can exceed 100%, while the current guardrail requires at most 100%; #98 must resolve contract/test semantics before this panel is published. Never clamp or redefine it in BI. |
| Q03 / P0 | What fraction of daily alerts is high severity or linked to cases? | Executive / Fraud Operations | Canonical daily `high_severity_alert_rate_pct`, `fraud_case_open_rate_pct` and their available counts; validate alert/case uniqueness before trusting totals. |
| Q04 / P0 | Which severity, status, queues and owning teams contain alert activity? | Fraud Operations | Gold alert rows with `alert_severity`, `alert_status`, `queue_code`, owning team/business unit and case context. Use Gold status values and validated alert grain; a current status distribution is not a historical backlog trend. |
| Q05 / P1 | What does the existing SLA flag say about case opening? | Fraud Operations | `is_sla_breached` describes case opening after the due time; it is null without the required case/open timestamps. Label that scope and show missing coverage; do not present it as a live overdue-open-alert or resolution-SLA measure. |
| Q06 / P0 | How do transaction status, reversal and cross-border mix vary? | Analyst | Gold transaction status and `is_reversal`/`is_cross_border` flags; compare counts. Existing daily `reversal_rate_pct` is global/day only; new period or dimensional ratios require governed Gold support. |
| Q07 / P0 | Which channels and rails account for transaction activity? | Analyst | Transaction-grain counts, Gold channel-event lookup and `payment_rail_code`; validate lookup uniqueness and unknown-channel handling before cross-filtering. |
| Q08 / P1 | What is the current build-wide high-risk-event and open alert/case posture? | Executive | Existing portfolio snapshot rates/counts, clearly labeled whole-build coverage. Not an event-date-filtered KPI or a historical time series; validate cross-model coverage before comparison. |
| Q09 / P1, currency gate | What financial loss/recovery or transaction amount can be reported safely? | Executive / Analyst | Amounts only with demonstrated currency/coverage semantics. Transaction amounts must stay grouped by their own currency; current global loss/recovery aggregates and recovery rates are blocked until a single-currency or governed currency-aware contract is proven. |

Every implemented visual must retain its question ID, model/field lineage, declared grain and comparison/reconciliation evidence. No invented target, alert threshold, financial materiality limit or benchmark is implied by these questions. Business targets remain an explicit future owner decision.

## Dashboard scope and controls

Deliver three read-only pages (#95–#97), with supporting drill-through inside those pages. Initial P0 visuals use reconciled counts and Gold flags; definition/currency-gated ratios or financial visuals stay unavailable until their gates pass. Empty, unavailable and filtered-out states must differ from a measured zero. No BI product is selected by this design: #94 must demonstrate a compatible local connection and no-cost operation before any dashboard is called live.

| Page | Default scope | Allowed filters and limits |
| --- | --- | --- |
| Executive KPI | Daily portfolio activity, with a separately labeled build-wide risk snapshot if qualified. | Date on daily series only. Daily and snapshot KPIs do not support channel/team/region/currency breakdowns. Snapshot cards must ignore unsupported date filters visibly, or be isolated from those controls. |
| Fraud Operations | Alert-created-date activity and current recorded alert/case context. | Date, severity, status, queue, owning business unit and analyst team. Operational region means owning business-unit region; not customer residency or transaction origin. Validate lookup uniqueness and optional/null relationships. |
| Transaction & Channel Analysis | Transaction-date activity with channel and payment context. | Date, channel, rail, transaction status, cross-border/reversal flags; transaction currency for amounts. Geographic origin uses channel branch to branch region where present; non-branch/unknown origin remains explicit, without fallback to customer residency. |

There is no universal cross-page region/team/batch filter. A filter must have a documented route at that visual's grain and must not silently affect only part of a ratio. UTC-derived transaction, alert-created and payment-event dates have separate business meanings. Date windows and available source coverage must be visible; default to the complete validated demo coverage until actual data is inspected under #94/#99.

Aggregated daily/portfolio audit `ingestion_batch_id` fields are not reliable batch-slicing dimensions: daily rows combine sources and the snapshot uses aggregate metadata. Source timestamps/build IDs support provenance; a build timestamp alone does not establish freshness, completeness or successful pipeline execution. Actual data/build/quality checks remain required before demonstration.

Exclude production decisions, case/alert write-back, PII/customer-identity browsing, automated fraud decisions, real-time streaming, ML evaluation/accuracy claims, historical snapshot trends without stored snapshots, unsupported FX conversion and Snowflake/cloud deployment claims. No new paid service, paid BI connector or test/prod infrastructure is in scope. Snowflake stays the conceptual target; this owner's portfolio uses the existing Docker Spark/Hive Gold runtime and synthetic data.

## Acceptance and delivery handoff

- #94: select compatible no-cost BI/local access; demonstrate schema visibility, required Gold columns, row/key quality, read-only access and connection stability. A file-backed fallback must be labeled with export time/run provenance and must not be called a live database connection.
- #95–#97: implement the named audience pages and Q IDs; publish only visuals whose grain, classification, label, filter and currency gates are resolved. Preserve source lineage and synthetic-data notice.
- #98: reconcile to dbt outputs at the declared grain, align known SQL/glossary/schema/test disagreements, validate join fan-out/coverage, period aggregation and currency rules. New business logic belongs in reviewed Gold/dbt changes, not duplicated BI calculations.
- #99: demonstrate understandable filters/drill-through, explicit unsupported/unknown/empty states and measured local-demo performance. Establish thresholds with the owner using measured data, not an invented SLA.
- #100: document connection/configuration, source mapping, refresh/provenance, dashboard navigation, screenshots/demo and all remaining limitations. Secrets stay local; reports/exports must contain only approved synthetic content.

Issue #93 is a design deliverable. Its completion does not complete #94–#100, prove materialized Gold availability, implement a BI connection or validate dashboard numbers. Phase 8 CI passing and closed issue states do not establish those runtime outcomes. PR #129 remains the separate pending Phase 8 documentation follow-up.
