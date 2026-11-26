# Analytics

Phase 9 defines the business-facing consumption layer over governed dbt Gold outputs. Start with the [analytics use cases and dashboard scope](use-cases-dashboard-scope.md).

Use the [Gold model/metric/filter mapping](gold-model-mapping.md) before designing a visual, and the [Phase 9 delivery plan](../documents/phase-9-plan/README.md) for workstream dependencies and acceptance. Known definition, grain and currency gaps are explicit gates for downstream reconciliation.

The portfolio reuses local Docker Spark/Hive and synthetic data, with no paid cloud resources. Snowflake remains a target architecture; a local demo is not a Snowflake qualification. BI connection and dashboard implementations follow the scope design under issues #94–#100; no live BI connection or finished dashboard is claimed by issue #93.
