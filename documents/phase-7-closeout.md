# Phase 7 closeout

Validation date: November 16, 2026 (America/New_York). UTC timestamps in the evidence fall on November 17.

Phase 7 implementation is delivered on `observability-lineage` for review and merge to `main`. The canonical handoff is [Phase 7 — Observability and Lineage](phase-7-observability-lineage.md). Original workstream plans remain in `phase-7-plan/`.

## Live local integration evidence

The `fraudlens` Data-Lab container ran PostgreSQL, Marquez API/web, Prometheus, and Grafana. No Data-Lab source changes are required by this branch. Runtime configuration and test data stay local.

| Check | Result |
| --- | --- |
| Marquez API health | `/api/v1/namespaces` returned HTTP 200. |
| dbt delivery | 61 manifest-derived model events validated in dry-run mode and delivered with HTTP 201. |
| dbt job isolation | All 61 jobs have unique run UUIDs and inputs/outputs matching their own manifest events. |
| Airflow correlation | An ingestion metadata event was delivered; the original pipeline ID was recovered from its run facet. |
| Marquez visualization | Browser inspection confirmed the verified namespace, job list, and upstream/downstream graph for `dim_account`. |
| Grafana | All five FraudLens dashboards imported; datasource UID `prometheus` passed its health check. |
| Prometheus | A representative query for each dashboard returned a series: run status `1`, stage duration `42.5`, failure count `0`, exporter health `1`, lineage count `61`. |

Detailed job identities, inputs, outputs, dashboard UIDs, and query results are in [runtime-validation.json](evidence/phase-7/runtime-validation.json). Screenshots: [Marquez jobs](evidence/phase-7/marquez-jobs.png), [Marquez lineage](evidence/phase-7/marquez-lineage.png), and [Grafana pipeline overview](evidence/phase-7/grafana-pipeline-overview.png).

The lineage namespace is `fraudlens.phase7.verified`. An earlier exploratory namespace, `fraudlens.phase7.closeout`, exposed shared-run contamination; it is excluded from accepted evidence. OpenLineage run IDs are now deterministic UUIDs scoped to namespace, job, and pipeline execution. Original pipeline IDs remain in facets for correlation. The identity requirement follows the [OpenLineage object model](https://openlineage.io/docs/spec/object-model/).

Closeout also corrected API/UI endpoint defaults, timeout reporting, Data-Lab datasource ports, and JSON health endpoints incorrectly configured as Prometheus scrape targets. The metric adapter now maps every FraudLens metric referenced by the shipped dashboards; a regression check renders those sources and verifies that none are skipped. Individual metric sources still need to emit events or have an exporter enabled.

## Reproduce

Start the required runtime services:

```powershell
docker exec -u datalab fraudlens bash /home/datalab/app/tech/lineage/manage.sh start
docker exec -u datalab fraudlens bash /home/datalab/app/tech/monitoring/manage.sh start
docker port fraudlens
```

Current Windows host ports are Marquez API `5002`, Marquez UI `3004`, Grafana `3005`, and Prometheus `9098`. Their container-local ports are `5000`, `3000`, `3001`, and `9095` respectively. Configure Grafana datasource UID `prometheus` to `http://127.0.0.1:9095` inside Data-Lab and import `monitoring/grafana/dashboards/*.json`.

Export the current dbt manifest using an execution ID, dry-run delivery, then send to the full ingestion endpoint:

```powershell
py dbt/scripts/export_openlineage_from_manifest.py --manifest dbt/target/manifest.json --output airflow/artifacts/phase7-closeout/lineage.jsonl --namespace fraudlens.phase7.verification --run-id manual-phase7-verification --batch-id metadata_only
py scripts/check_marquez_health.py --base-url http://127.0.0.1:5002
py scripts/deliver_openlineage_to_marquez.py --input airflow/artifacts/phase7-closeout/lineage.jsonl --url http://127.0.0.1:5002/api/v1/lineage
py scripts/deliver_openlineage_to_marquez.py --input airflow/artifacts/phase7-closeout/lineage.jsonl --url http://127.0.0.1:5002/api/v1/lineage --send
py scripts/validate_observability_lineage_coverage.py
py -m pytest tests airflow/tests -q
```

Use the [Prometheus storage verification guide](../monitoring/prometheus/storage-verification.md) to expose rendered metric text through a Prometheus-compatible HTTP endpoint. Serve UTF-8 text with LF line endings and `Content-Type: text/plain; version=0.0.4`; CRLF output is rejected by the tested Prometheus parser. The smoke test used an isolated fixture endpoint on container-local port `9110` and a separate scrape job; it did not replace the Data-Lab base scrape jobs. Health JSON endpoints must be checked separately, rather than scraped as Prometheus text.

The full suite passed in an archive of the staged repository without private local configuration: **71 tests and 127 subtests**. The coverage validator passed with five critical services, three pipeline layers, and no missing evidence paths.

## Validation boundaries and handoff

- These are local integration smoke checks using existing dbt manifest metadata and synthetic metric fixtures. No fresh warehouse transformation or production deployment is claimed.
- Optional runtime CPU/memory exporters and external alert routing remain operational hardening work. Empty panels for unavailable sources are expected and documented.
- The local full-suite run must use a clean checkout without private `.env` or `synthetic_generator/runtime_config.yaml`: the Phase 2 generator tests load these files into process environment, which can affect the missing-MinIO-configuration test.
- Review and merge the Phase 7 pull request before starting Phase 8 CI/CD from `main`. Closing implementation issues records delivery on the feature branch; it does not record a merge or deployment.
