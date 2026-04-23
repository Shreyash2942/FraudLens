# Synthetic Generator

This package contains the Phase 2 synthetic data batch generator for FraudLens.

## CLI

Run from the repository root:

```powershell
py -m synthetic_generator.generate --mode mixed --output-dir data --days 90 --profile medium_demo --seed 42 --validate
```

Curated blueprint mode:

```powershell
py -m synthetic_generator.generate --mode blueprint --blueprint hybrid_fraud_ops_demo --output-dir data --profile medium_demo --seed 42 --validate
```

List built-in blueprints:

```powershell
py -m synthetic_generator.generate --list-blueprints
```

## Batch Output Layout

Generated batch artifacts are written under:

- `data/batches/<batch_id>/landing/csv/*.csv`
- `data/batches/<batch_id>/control/manifest.json`
- `data/batches/<batch_id>/control/batch_control.json`
- `data/batches/<batch_id>/quality/validation_report.json`

This keeps the generator code separate from the generated dataset artifacts.

The generator now emits 21 CSV datasets:

- 14 core banking and fraud-ops datasets
- 7 supporting calendar, geography, and organization datasets for dashboard control

## Blueprint Support

Built-in curated YAML blueprints live under `synthetic_generator/blueprints/` and drive:

- exact scenario counts
- lifecycle targets
- decision and disposition mixes
- realism emphasis flags
- calendar controls for year and month shaping
- geography and organization mixes for region, branch territory, business unit, and analyst team
- customer segment and payment rail controls
- fraud-ops controls such as alert source, case priority, decision reason, and recovery status
- blueprint compliance validation
