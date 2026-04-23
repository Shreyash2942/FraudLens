# Data

This directory is the output-only location for Phase 2 synthetic dataset batches produced by either mixed mode or blueprint-curated mode.

## Contents

- `batches/` local batch-run root for generated datasets, control files, and quality reports

## Output Convention

Generated batch runs should be written under:

- `data/batches/<batch_id>/landing/csv/*.csv`
- `data/batches/<batch_id>/control/manifest.json`
- `data/batches/<batch_id>/control/batch_control.json`
- `data/batches/<batch_id>/quality/validation_report.json`

These generated artifacts are ignored by Git.

The generator CLI now lives in the repo-root `synthetic_generator/` package and prints stage progress and periodic counters during longer runs so local batch execution is easier to monitor.

Curated YAML blueprints live separately under `synthetic_generator/blueprints/`; generated data never mixes with generator source code.

Each generated batch now includes control and summary artifacts that are useful for dashboard-focused inspection:

- scenario and lifecycle summaries in `control/manifest.json`
- org and geography summaries in `control/manifest.json`
- control settings and stage timings in `control/batch_control.json`
