# Dashboard-to-Gold model mapping

Issue [#93](https://github.com/Shreyash2942/FraudLens/issues/93), November 25, 2026. Implements the source alignment for [Q01–Q09 and the dashboard scope](use-cases-dashboard-scope.md). This is static source inspection, not a claim that tables are populated, a BI connector works or values have been reconciled.

## Existing model inventory and allowed use

dbt node names and configured aliases below come from SQL. Actual catalog/schema/identifier visibility must be taken from the built manifest and verified in #94; the `gold/` directory does not itself prove a physical `GOLD` schema or case-sensitive table name.

| dbt node / SQL source | Configured alias | Intended grain / identifiers | Questions and limits |
| --- | --- | --- | --- |
| [`fact_transactions`](../dbt/models/gold/facts/fact_transactions.sql) | `gold_fact_transactions` | Transaction; `payment_transaction_id`, surrogate `fact_transaction_sk` uses transaction + instruction IDs. | Q06/Q07; Q09 amounts only by verified transaction currency. Use transaction date/status/flags and channel-event key. Payment-level fraud/case counts repeat across multiple transactions: do not sum them to obtain unique alerts/cases. |
| [`fact_fraud_alerts`](../dbt/models/gold/facts/fact_fraud_alerts.sql) | `gold_fact_fraud_alerts` | Intended alert; `fraud_alert_id`, surrogate `fact_fraud_alert_sk` uses alert + risk IDs. | Q04/Q05 and source for Q01/Q03/Q09. Case/disposition joins require uniqueness/fan-out checks before aggregates. Repeated case amounts or multiple cases must not inflate alert totals. |
| [`fact_payment_events`](../dbt/models/gold/facts/fact_payment_events.sql) | `gold_fact_payment_events` | Payment instruction; `payment_instruction_id`, `fact_payment_event_sk`. | Q08 risk/alert/case rollups and payment context. Transaction counts differ from payment-event counts. Pre-summed booking amounts do not acquire a valid currency merely by selecting instruction currency. |
| [`fact_daily_fraud_metrics`](../dbt/models/gold/facts/fact_daily_fraud_metrics.sql) | `gold_fact_daily_fraud_metrics` | One `metric_date`; independent transaction-date, alert-created-date and payment-event-date aggregates. | Q01 and KPI source. Existing dates come from observed metric dates joined to the calendar, not a complete zero-filled calendar. No channel/team/region/currency grain; aggregate audit metadata is not a safe batch filter. |
| [`kpi_daily_fraud_operations`](../dbt/models/gold/kpi/kpi_daily_fraud_operations.sql) | `gold_kpi_daily_fraud_operations` | One `metric_date`; daily global portfolio. | Q01/Q02/Q03 and global daily reversal context for Q06. Q09 recovery is currency-gated. Do not attach lower-grain detail to these rows or pretend dimensional filters apply. |
| [`kpi_portfolio_risk_snapshot`](../dbt/models/gold/kpi/kpi_portfolio_risk_snapshot.sql) | `gold_kpi_portfolio_risk_snapshot` | One row per build; `snapshot_at_utc` is build time, not a retained historical snapshot key. | Q08 and gated Q09; rolls all available payment events and daily aggregates together. It is not date-sliceable or an additive sequence of historical snapshots. |

## Reuse existing KPI logic

[The KPI glossary](../dbt/models/gold/kpi/KPI_GLOSSARY.md), [lineage](../dbt/models/gold/kpi/KPI_LINEAGE.md), SQL and [`kpi_metrics.sql`](../dbt/macros/kpi_metrics.sql) are the governed sources. Current SQL uses `fraudlens_pct`: zero/null denominator yields zero, and values are multiplied by 100. The macro is not inherently bounded. Keep zero-denominator coverage visible alongside the source-defined value.

| Question | Existing fields / calculation in Gold | Publication gate |
| --- | --- | --- |
| Q01 | Daily `total_transactions`, `total_fraud_alerts`; counts align to their respective activity dates. | Validated daily grain, coverage and calendar visibility; no missing-day completeness claim. |
| Q02 | `alert_rate_pct` = daily alert count / transaction count × 100. | Resolve alert-to-transaction meaning and 0–100 guardrail conflict under #98; no BI clamp or relabeling as confirmed fraud incidence. |
| Q03 | `high_severity_alert_rate_pct` = high-severity alerts / all alerts × 100; `fraud_case_open_rate_pct` = alerts with cases / all alerts × 100. | Resolve schema prose and verify alert/case uniqueness; linked-case presence is not a measured investigation completion rate. |
| Q04/Q05 | Alert status/severity/queue/owning IDs, `fraud_case_id`, case timestamps and `is_sla_breached`. | Use source classifications, unique alert grain and explicitly nullable case-open SLA semantics; no new live overdue/age KPI. |
| Q06 | Transaction `is_reversal`, `is_cross_border`, status; global daily `reversal_rate_pct` = reversed transaction count / total transactions × 100. | Correct schema prose for reversal denominator. Counts can be sliced at transaction grain; new dimensional or period rates require reviewed Gold output. |
| Q07 | Transaction keys, `channel_event_id`, `payment_rail_code`, channel lookup `channel_code`. | Validate many-to-one channel-event join; preserve unknown channel/origin and reconcile counts before/after join. |
| Q08 | Snapshot `high_risk_payment_event_rate_pct`, `open_alert_backlog_rate_pct`, `open_case_backlog_rate_pct`, `cross_border_transaction_rate_pct` and their counts. | Whole-build coverage and consistent source universe; current recorded statuses are not historical as-of backlog. |
| Q09 | Daily `recovery_rate_pct`; snapshot `portfolio_recovery_rate_pct`; transaction `booking_amount` with `transaction_currency_code`. | Prove monetary currency/cohort alignment first; no all-currency financial headline or implicit FX conversion. |

The [KPI schema prose](../dbt/models/gold/kpi/gold_kpi_models.yml) currently describes high-severity rate using transactions and reversal rate using alerts; their SQL denominators are alerts and transactions respectively. The [rate guardrail](../dbt/tests/gold/test_kpi_rate_guardrails.sql) also bounds alert rate at 100 although count-based SQL can exceed it. These are **known reconciliation/definition gates**, not corrections completed by #93. #98 must align business acceptance, SQL/glossary/schema/tests before affected panels are published; the dashboard must not silently pick a conflicting definition.

Across several days, counts may be summed only after validating disjoint daily grain. Never sum or average daily percentages to invent a period KPI, and never sum snapshot rates. Period/dimensional KPIs need governed Gold outputs that reuse centralized ratio semantics; those outputs are not currently present. Static columns or passing offline CI do not supply that evidence.

## Dimension routes and join safety

| Visual context | Existing route | Constraint |
| --- | --- | --- |
| Calendar | Transaction `transaction_date`, alert `alert_created_date`, payment `payment_event_date`, daily `metric_date` → [`dim_date.calendar_date`](../dbt/models/gold/dimensions/dim_date.sql). | Distinct activity clocks; no synthetic common fraud-event cohort implied by matching dates. |
| Channel | Transaction/payment `channel_event_id` → [`dim_channel.channel_event_id`](../dbt/models/gold/dimensions/dim_channel.sql), then group by its `channel_code`. | The dimension is event-grained, not one row per channel code. Joining on code fans out; use the actual event key. |
| Fraud ownership | Alert `owning_business_unit_id` → [`dim_business_unit.business_unit_id`](../dbt/models/gold/dimensions/dim_business_unit.sql); `owning_analyst_team_id` → [`dim_analyst_team.analyst_team_id`](../dbt/models/gold/dimensions/dim_analyst_team.sql). | Default operational region is business-unit `region_id`; team region is a separate attribution, not an interchangeable global filter. |
| Transaction origin | Channel `branch_id` → [`dim_branch.branch_id`](../dbt/models/gold/dimensions/dim_branch.sql) → [`dim_region.region_id`](../dbt/models/gold/dimensions/dim_region.sql). | Null/non-branch channels remain unknown/not applicable. Do not fall back to customer residency. |
| Customer organization | [`dim_customer`](../dbt/models/gold/dimensions/dim_customer.sql) contains a latest-ranked assignment; [`dim_customer_org_assignment`](../dbt/models/gold/dimensions/dim_customer_org_assignment.sql) contains role and effective intervals. | Latest-ranked is not proven event-time attribution. Do not join assignment history on customer ID alone. Historical attribution needs a governed time/role-aware Gold route and non-overlap validation before use. It is outside initial P0 filters. |

Do not join facts directly to each other at incompatible grain. Join only unique dimensions after testing row-count and measure preservation; null relationships must remain visible. Existing [fact/dimension relationship tests](../dbt/tests/gold/test_fact_dimension_relationships.sql), [fact schema/unique tests](../dbt/models/gold/facts/gold_fact_models.yml), [assignment overlap test](../dbt/tests/gold/test_dim_customer_org_assignment_no_overlap.sql) and [controlled KPI scenarios](../dbt/tests/validation/test_kpi_controlled_scenarios.sql) are starting validation assets, not proof of a successful fresh warehouse run.

## Source readiness and downstream handoff

Money in daily/portfolio models lacks currency grain and case loss/recovery must not inherit a transaction currency by inference. Single-currency demo qualification or a reviewed currency-aware Gold extension is required for Q09, including recovery ratios; label that assumption and preserve its evidence.

[`gold_exposures.yml`](../dbt/models/gold/gold_exposures.yml) already declares fraud-operations and portfolio-risk consumption dependencies. Its example URLs/maturity metadata are not a deployed dashboard or proven connection. Dashboard implementations/exposure links must be reconciled in #95–#100.

For #94/#98, capture actual target/catalog/schema/aliases, dbt build/run and batch coverage, unique keys, source row counts, missing joins, before/after join totals, canonical KPI outputs and each visual's filter behavior. Include currency/definition gates and nullable/zero-denominator cases. Keep credentials local; no service or warehouse query was executed to produce this design mapping.
