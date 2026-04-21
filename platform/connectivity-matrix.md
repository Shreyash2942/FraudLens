# FraudLens Connectivity Matrix

This matrix shows how future FraudLens subsystems depend on the external platform capabilities sourced from `Shreyash2942/Data-Lab`.

| FraudLens subsystem | Airflow | PostgreSQL | MinIO | Prometheus | Grafana | Marquez | OpenLineage |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Orchestration control plane | Required | Required | Optional | Optional | Optional | Optional | Required |
| Raw data landing | Optional | Optional | Required | Optional | Optional | Optional | Optional |
| Synthetic data exchange | Optional | Optional | Required | Optional | Optional | Optional | Optional |
| Transformation execution | Required | Optional | Optional | Optional | Optional | Optional | Required |
| Monitoring and health | Optional | Optional | Optional | Required | Required | Optional | Optional |
| Lineage visibility | Optional | Optional | Optional | Optional | Optional | Required | Required |
| Warehouse loading coordination | Required | Optional | Required | Optional | Optional | Optional | Optional |

## Interpretation

- Airflow is the orchestrating entry point for future pipeline work.
- PostgreSQL is the metadata dependency that supports orchestration and possibly additional platform metadata use cases.
- MinIO is the expected object landing zone for files and staged assets.
- Prometheus and Grafana form the monitoring pair.
- Marquez and OpenLineage form the lineage pair.

The runtime may currently package these capabilities inside one actual container, and that is acceptable for this portfolio project. FraudLens still documents them separately so later phases can target stable interfaces and keep the Snowflake-target architecture understandable.
