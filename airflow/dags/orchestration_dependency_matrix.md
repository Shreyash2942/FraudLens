# Orchestration Dependency Matrix

Master DAG: `fraudlens_pipeline_orchestration`

## Stage Order

1. `prepare_runtime`
2. `ingestion_layer`
3. `ingestion_complete_gate`
4. `transformation_layer`
5. `transformation_complete_gate`
6. `validation_layer`
7. `publish_run_artifacts`

## Gate Contract

- `ingestion_complete_gate` blocks transformation until ingestion path is complete.
- `transformation_complete_gate` blocks validation until transformation path is complete.
- publish stage runs only after validation path completion.
