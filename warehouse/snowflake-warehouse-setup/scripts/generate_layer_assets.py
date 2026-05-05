from __future__ import annotations

import argparse
import json
from pathlib import Path

from _config_loader import load_profile
from _dataset_layout import (
    DATASET_ORDER,
    bronze_batch_stage_path,
    bronze_table_name,
    gold_table_name,
    layer_spark_job_file_name,
    layer_sql_file_name,
    silver_table_name,
    table_columns,
    table_data_columns,
)

ROOT = Path(__file__).resolve().parents[1]
SQL_ROOT = ROOT / "sql"
SPARK_ROOT = ROOT / "spark"


def _warehouse_context(profile_name: str | None) -> dict[str, str]:
    profile = load_profile(profile_name)
    warehouse = profile.get("warehouse", {})
    schemas = warehouse.get("schemas", {})
    return {
        "database": str(warehouse.get("database", "FRAUDLENS")).upper(),
        "bronze_schema": str(schemas.get("bronze", "BRONZE")).upper(),
        "silver_schema": str(schemas.get("silver", "SILVER")).upper(),
        "gold_schema": str(schemas.get("gold", "GOLD")).upper(),
        "file_format_name": str(warehouse.get("file_format_name", "FF_BRONZE_CSV_V1")).upper(),
        "external_stage_name": str(warehouse.get("external_stage_name", "STG_BRONZE_MINIO_RAW")).upper(),
    }


def _layer_schema(layer: str, context: dict[str, str]) -> str:
    if layer == "bronze":
        return context["bronze_schema"]
    if layer == "silver":
        return context["silver_schema"]
    return context["gold_schema"]


def _layer_table_name(layer: str, dataset: str) -> str:
    if layer == "bronze":
        return bronze_table_name(dataset)
    if layer == "silver":
        return silver_table_name(dataset)
    return gold_table_name(dataset)


def _render_bronze_ddl(database: str, schema: str, dataset: str) -> str:
    table_name = bronze_table_name(dataset)
    column_lines = [f"  {name} {snowflake_type}" for name, snowflake_type in table_columns(dataset)]
    column_lines.extend(
        [
            "  INGESTION_BATCH_ID VARCHAR",
            "  SOURCE_FILE_NAME VARCHAR",
            "  INGESTED_AT_UTC TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()",
        ]
    )
    joined = ",\n".join(column_lines)
    return (
        f"-- Auto-generated Bronze DDL for dataset: {dataset}\n"
        f"CREATE TABLE IF NOT EXISTS {database}.{schema}.{table_name} (\n"
        f"{joined}\n"
        ");\n"
    )


def _render_bronze_dml(database: str, schema: str, file_format_name: str, stage_name: str, dataset: str) -> str:
    table_name = bronze_table_name(dataset)
    data_columns = table_data_columns(dataset)
    load_columns = ",\n  ".join(data_columns + ["INGESTION_BATCH_ID", "SOURCE_FILE_NAME", "INGESTED_AT_UTC"])
    projected_fields = ",\n    ".join([f"t.${index}" for index in range(1, len(data_columns) + 1)])
    stage_path = bronze_batch_stage_path(dataset, "$BATCH_ID")
    return (
        f"-- Auto-generated Bronze COPY INTO for dataset: {dataset}\n"
        "SET BATCH_ID = '<replace_with_batch_id>';\n\n"
        f"COPY INTO {database}.{schema}.{table_name} (\n"
        f"  {load_columns}\n"
        ")\n"
        "FROM (\n"
        "  SELECT\n"
        f"    {projected_fields},\n"
        "    $BATCH_ID,\n"
        "    METADATA$FILENAME,\n"
        "    CURRENT_TIMESTAMP()\n"
        f"  FROM @{database}.{schema}.{stage_name}/{stage_path} (FILE_FORMAT => {database}.{schema}.{file_format_name}) t\n"
        ")\n"
        "ON_ERROR = 'ABORT_STATEMENT';\n"
    )


def _render_scaffold_ddl(layer: str, database: str, schema: str, dataset: str) -> str:
    table_name = _layer_table_name(layer, dataset)
    return (
        f"-- Scaffold-only {layer.upper()} DDL for dataset: {dataset}\n"
        "-- TODO: replace placeholder columns with curated model design.\n"
        f"CREATE TABLE IF NOT EXISTS {database}.{schema}.{table_name} (\n"
        "  PLACEHOLDER_RECORD_ID VARCHAR,\n"
        "  SOURCE_BATCH_ID VARCHAR,\n"
        "  PIPELINE_CREATED_AT_UTC TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()\n"
        ");\n"
    )


def _render_scaffold_dml(layer: str, database: str, schema: str, dataset: str) -> str:
    table_name = _layer_table_name(layer, dataset)
    dependency_table = bronze_table_name(dataset) if layer == "silver" else silver_table_name(dataset)
    dependency_schema = "BRONZE" if layer == "silver" else "SILVER"
    return (
        f"-- Scaffold-only {layer.upper()} DML for dataset: {dataset}\n"
        "-- TODO: replace placeholder select with curated transform logic.\n"
        "SET BATCH_ID = '<replace_with_batch_id>';\n\n"
        f"INSERT INTO {database}.{schema}.{table_name} (\n"
        "  PLACEHOLDER_RECORD_ID,\n"
        "  SOURCE_BATCH_ID\n"
        ")\n"
        "SELECT\n"
        "  'TODO_RECORD_ID',\n"
        "  $BATCH_ID\n"
        f"FROM {database}.{dependency_schema}.{dependency_table}\n"
        "WHERE INGESTION_BATCH_ID = $BATCH_ID\n"
        "LIMIT 1;\n"
    )


def _render_spark_job(layer: str, dataset: str) -> str:
    return f"""from __future__ import annotations

import sys
from pathlib import Path

COMMON_PATH = Path(__file__).resolve().parents[2] / "common"
if str(COMMON_PATH) not in sys.path:
    sys.path.insert(0, str(COMMON_PATH))

from dataset_job_contract import parse_common_args, run_with_contract

EXPECTED_LAYER = "{layer}"
EXPECTED_DATASET = "{dataset}"


def execute(args):
    if args.layer != EXPECTED_LAYER:
        return {{"status": "failed", "row_count": -1, "error_message": f"Layer mismatch: {{args.layer}} != {{EXPECTED_LAYER}}"}}
    if args.dataset != EXPECTED_DATASET:
        return {{"status": "failed", "row_count": -1, "error_message": f"Dataset mismatch: {{args.dataset}} != {{EXPECTED_DATASET}}"}}
    return {{
        "status": "scaffold",
        "row_count": 0,
        "error_message": "",
    }}


def main() -> int:
    args = parse_common_args(description="FraudLens {layer} dataset job: {dataset}")
    return run_with_contract(args, execute)


if __name__ == "__main__":
    raise SystemExit(main())
"""


def _index_payload(layer: str, dataset_order: list[str]) -> dict[str, object]:
    requires = [] if layer == "bronze" else ["bronze"]
    enabled_default = layer == "bronze"
    return {
        "layer": layer,
        "enabled_default": enabled_default,
        "dependency_policy": "bronze_strict",
        "requires_layers": requires,
        "datasets": [
            {
                "order": i + 1,
                "dataset": dataset,
                "sql_ddl_path": f"sql/{layer}/ddl/{layer_sql_file_name(layer, dataset)}",
                "sql_dml_path": f"sql/{layer}/dml/{layer_sql_file_name(layer, dataset)}",
                "spark_job_path": f"spark/{layer}/jobs/{layer_spark_job_file_name(layer, dataset)}",
            }
            for i, dataset in enumerate(dataset_order)
        ],
    }


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_index_files(layer: str, datasets: list[str]) -> None:
    layer_dir = SQL_ROOT / layer
    index_json = _index_payload(layer, datasets)
    _write(layer_dir / "dataset_index.json", json.dumps(index_json, indent=2) + "\n")
    _write(layer_dir / "_index_ordered.txt", "\n".join(datasets) + "\n")


def _clean_generated_layer_files(layer: str) -> None:
    for base in [SQL_ROOT / layer / "ddl", SQL_ROOT / layer / "dml", SPARK_ROOT / layer / "jobs"]:
        if not base.exists():
            continue
        for path in base.glob(f"{layer}__*"):
            if path.is_file():
                path.unlink()


def _emit_layer_assets(layer: str, context: dict[str, str], emit_spark_jobs: bool) -> None:
    database = context["database"]
    schema = _layer_schema(layer, context)
    datasets = list(DATASET_ORDER)

    for dataset in datasets:
        file_name = layer_sql_file_name(layer, dataset)
        if layer == "bronze":
            ddl_sql = _render_bronze_ddl(database, schema, dataset)
            dml_sql = _render_bronze_dml(
                database,
                schema,
                context["file_format_name"],
                context["external_stage_name"],
                dataset,
            )
        else:
            ddl_sql = _render_scaffold_ddl(layer, database, schema, dataset)
            dml_sql = _render_scaffold_dml(layer, database, schema, dataset)
        _write(SQL_ROOT / layer / "ddl" / file_name, ddl_sql)
        _write(SQL_ROOT / layer / "dml" / file_name, dml_sql)
        if emit_spark_jobs:
            job_name = layer_spark_job_file_name(layer, dataset)
            _write(SPARK_ROOT / layer / "jobs" / job_name, _render_spark_job(layer, dataset))

    _write_index_files(layer, datasets)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate layer-first dataset SQL and Spark job assets.")
    parser.add_argument(
        "--layers",
        default="bronze",
        help="Comma-separated layers to generate. Values: bronze,silver,gold or all.",
    )
    parser.add_argument("--profile", choices=["local", "cloud"], default=None, help="Config profile override.")
    parser.add_argument("--emit-spark-jobs", action="store_true", help="Also generate per-dataset Spark job templates.")
    parser.add_argument("--clean", action="store_true", help="Remove previously generated layer files before emit.")
    return parser.parse_args()


def _resolve_layers(raw: str) -> list[str]:
    selected = [x.strip().lower() for x in raw.split(",") if x.strip()]
    if selected == ["all"]:
        return ["bronze", "silver", "gold"]
    invalid = [x for x in selected if x not in {"bronze", "silver", "gold"}]
    if invalid:
        raise ValueError(f"Unsupported layers: {', '.join(invalid)}")
    return selected or ["bronze"]


def main() -> int:
    args = parse_args()
    layers = _resolve_layers(args.layers)
    context = _warehouse_context(args.profile)

    for layer in layers:
        if args.clean:
            _clean_generated_layer_files(layer)
        _emit_layer_assets(layer, context, emit_spark_jobs=args.emit_spark_jobs)
        print(f"Generated assets for layer={layer}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
