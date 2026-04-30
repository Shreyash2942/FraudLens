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

Upload generated artifacts to MinIO:

```powershell
py -m synthetic_generator.generate --mode mixed --output-dir data --profile small_fast --seed 42 --upload-minio
```

## MinIO Configuration

The upload stage reads either FraudLens-native `MINIO_*` variables or Data-Lab-compatible
`DATALAB_MINIO_*` variables.

The generator auto-loads a project `.env` file (current working directory first, then repo root)
before parsing CLI arguments, so you can keep MinIO settings in `.env` and avoid exporting each run.
It also auto-loads `synthetic_generator/runtime_config.yaml` when present.

Recommended setup for container drift:

1. copy `synthetic_generator/runtime_config.yaml.example` to `synthetic_generator/runtime_config.yaml`
2. update MinIO endpoint/keys/bucket in that YAML only
3. run generator normally without exporting MinIO vars

Optional explicit file override:

```powershell
py -m synthetic_generator.generate --runtime-config synthetic_generator/runtime_config.yaml --mode mixed --output-dir data --profile small_fast --seed 42 --validate --upload-minio
```

Supported variable mapping:

- endpoint: `MINIO_ENDPOINT` or `DATALAB_MINIO_ENDPOINT` or `DATALAB_MINIO_ENDPOINT_OUTSIDE`
- access key: `MINIO_ACCESS_KEY` or `DATALAB_MINIO_ACCESS_KEY`
- secret key: `MINIO_SECRET_KEY` or `DATALAB_MINIO_SECRET_KEY`
- bucket: `MINIO_DEFAULT_BUCKET` or `DATALAB_MINIO_BUCKET` (default: `fraudlensdata`)
- prefix root: `PHASE2_MINIO_PREFIX` (default: `fraudlens/synthetic_data/batches`)

Uploaded object layout (MinIO) uses professional folder names:

- `raw_zone/csv/*.csv` (mapped from local `landing/csv`)
- `governance/control/*.json` (mapped from local `control`)
- `governance/quality/*.json` (mapped from local `quality`)

Data-Lab / fraudlens container examples:

Inside container (service endpoint):

```bash
export DATALAB_MINIO_ENDPOINT=http://localhost:9004
export DATALAB_MINIO_ACCESS_KEY=minio_admin
export DATALAB_MINIO_SECRET_KEY=minioadmin
export DATALAB_MINIO_BUCKET=datalab
```

Outside container (host endpoint):

```powershell
$env:DATALAB_MINIO_ENDPOINT_OUTSIDE="http://localhost:9009"
$env:DATALAB_MINIO_ACCESS_KEY="minio_admin"
$env:DATALAB_MINIO_SECRET_KEY="minioadmin"
$env:DATALAB_MINIO_BUCKET="datalab"
```

Project `.env` example for inside-container runs:

```dotenv
DATALAB_MINIO_ENDPOINT=http://localhost:9004
DATALAB_MINIO_ACCESS_KEY=minio_admin
DATALAB_MINIO_SECRET_KEY=minioadmin
DATALAB_MINIO_BUCKET=fraudlensdata
PHASE2_MINIO_PREFIX=fraudlens/synthetic_data/batches
```

Project `runtime_config.yaml` example for inside-container runs:

```yaml
minio:
  endpoint: http://localhost:9004
  endpoint_outside: http://localhost:9009
  access_key: minio_admin
  secret_key: minioadmin
  region: us-east-1
  bucket: fraudlensdata
  prefix_root: fraudlens/synthetic_data/batches
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
