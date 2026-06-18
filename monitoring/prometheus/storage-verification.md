# Prometheus Storage Verification

Issue: `#76`  
Phase: `Phase 7 - Observability And Lineage`

Use these checks to prove that Prometheus is not only configured, but also scraping and retaining FraudLens metric samples.

## Target Health

Check Prometheus target health:

```powershell
Invoke-RestMethod http://localhost:9090/api/v1/targets
```

Expected result:

- `fraudlens_metrics_exporter` is present
- `health` is `up` for required local targets
- `lastScrape` is recent
- optional service targets are documented if unavailable

## Sample Query Checks

Run sample PromQL queries:

```powershell
Invoke-RestMethod "http://localhost:9090/api/v1/query?query=fraudlens_pipeline_run_status"
Invoke-RestMethod "http://localhost:9090/api/v1/query?query=fraudlens_pipeline_artifact_completeness"
Invoke-RestMethod "http://localhost:9090/api/v1/query?query=fraudlens_metric_adapter_events_parsed_total"
```

Expected result:

- query status is `success`
- result set is not empty after a representative metric artifact has been rendered or exposed
- sample timestamps are recent enough for the validation run

## Freshness Checks

Freshness protects against accidentally validating old samples.

Recommended evidence:

- local metric artifact path and timestamp
- adapter output timestamp or scrape timestamp
- Prometheus query timestamp
- `fraudlens_metric_adapter_events_parsed_total` value
- `fraudlens_metric_adapter_events_skipped_total` value

## Retention Notes

- Retention is controlled by the local Data-Lab Prometheus runtime.
- This repository documents required queries and target expectations, but does not own Prometheus disk retention settings.
- For CI, validate static scrape config and sample rendering instead of requiring live storage.

## Troubleshooting

| Symptom | Likely Cause | Check |
|---|---|---|
| target missing | scrape config not loaded | reload Prometheus config or restart Data-Lab Prometheus |
| target down | adapter or service not running | check target host/port and local service logs |
| query empty | no rendered/exposed metric samples | inspect latest JSONL metric artifact and adapter output |
| stale samples | old metric values retained | compare local artifact timestamp with Prometheus sample timestamp |
| skipped events high | malformed or unmapped metric events | inspect adapter skipped count and mapping contract |

