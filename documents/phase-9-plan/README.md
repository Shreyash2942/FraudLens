# Phase 9: Analytics & Dashboard

Parent: [#92](https://github.com/Shreyash2942/FraudLens/issues/92). Branch: `92-phase-9-analytics-dashboard`, based on validated main merge `9080111`.

Start with [analytics use cases and dashboard scope](../../analytics/use-cases-dashboard-scope.md), the issue #93 design. The owner requires a no-spend portfolio: reuse local Docker Spark/Hive Gold and synthetic data. Snowflake is an architectural target, not a provisioned or qualified BI source. Do not mark the original Snowflake wording complete based on a local demo.

The [Gold mapping](../../analytics/gold-model-mapping.md) records actual dbt aliases/grains and known definition/filter/currency gaps. In particular, current KPI schema descriptions and rate guardrails require reconciliation with SQL before affected panels can be published.

| Order | Issue | Delivery |
| --- | --- | --- |
| P0 | #93 | Audience, reporting questions, scope/controls and source-model mapping; four task commits. |
| P0 | #94 | Choose compatible no-cost BI and demonstrate read-only Gold access, schema visibility, key/data quality and stability. |
| P0 alongside build | #98 | Resolve known KPI contract/test/description and grain/currency gaps, then reconcile every published visual against dbt. |
| P1 | #95 | Executive daily activity and qualified build-wide portfolio context. |
| P1 | #96 | Fraud Operations alert/status/severity/ownership context. |
| P1 | #97 | Transaction & Channel Analysis at transaction grain. |
| P1 | #99 | Usability, filtering, drill-through and measured demo performance. |
| P1 | #100 | Analytics connection/usage/refresh/provenance documentation and portfolio handoff. |

Issue #93 identifies gates; it does not silently amend KPI SQL or tests. #98 may begin before dependent panels are published, despite its later issue number. Parent #92 remains open until actual access, dashboards, reconciliation, usability and documentation evidence exist. The separate Phase 8 documentation PR #129 is not merged by this phase's scope work.
