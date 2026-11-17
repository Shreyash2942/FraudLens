# Prometheus Service Targets

Issue: `#76`  
Phase: `Phase 7 - Observability And Lineage`

The scrape config in `prometheus.yml` includes the local targets FraudLens expects to validate in Data-Lab or through local synthetic probes.

## Target Catalog

| Job | Default Target | Purpose | Notes |
|---|---|---|---|
| `fraudlens_metrics_exporter` | `localhost:9108` | FraudLens pipeline metrics rendered from canonical metric artifacts | Primary Phase 7 target. |
| `prometheus` | `localhost:9095` | Prometheus self-health | Data-Lab container-local Prometheus port. |
| `airflow` | `localhost:9102` | Airflow StatsD/Prometheus metrics | Optional exporter; `/health` is JSON and cannot be scraped as Prometheus text. |
| `grafana` | `localhost:3001` | Grafana service health | Data-Lab container-local Grafana metrics endpoint. |
| `marquez` | `localhost:9217` | Marquez lineage service metrics | Optional metrics bridge; validate API health separately with `check_marquez_health.py`. |
| `mongodb` | `localhost:9216` | MongoDB artifact storage health | Requires exporter or compatible synthetic probe. |
| `spark_hive_runtime` | `localhost:9109` | Local Spark/Hive surrogate runtime health | Requires exporter or compatible synthetic probe. |

## Endpoint Rules

- Keep hostnames and ports configurable for local Data-Lab differences.
- Do not treat optional exporter targets as blockers for CI contract validation.
- Keep FraudLens pipeline metrics separate from generic Airflow service metrics.
- Prefer `service_name` labels from this catalog so Grafana service panels remain stable.
- Record unavailable optional targets as validation gaps or accepted local limitations in issue `#81`.

