from __future__ import annotations

import argparse
from pathlib import Path

from _config_loader import load_profile
from _dataset_layout import (
    DATASET_ORDER,
    bronze_batch_stage_path,
    bronze_table_name,
    table_data_columns,
)


def _warehouse_context(profile_name: str | None) -> dict[str, str]:
    profile = load_profile(profile_name)
    warehouse = profile.get("warehouse", {})
    schemas = warehouse.get("schemas", {})
    return {
        "database": str(warehouse.get("database", "FRAUDLENS")).upper(),
        "bronze_schema": str(schemas.get("bronze", "BRONZE")).upper(),
        "file_format_name": str(warehouse.get("file_format_name", "FF_BRONZE_CSV_V1")).upper(),
        "external_stage_name": str(warehouse.get("external_stage_name", "STG_BRONZE_MINIO_RAW")).upper(),
    }


def _copy_sql(database: str, schema: str, file_format_name: str, stage_name: str, dataset: str, batch_id: str) -> str:
    table_name = bronze_table_name(dataset)
    data_columns = table_data_columns(dataset)
    load_columns = ",\n  ".join(data_columns + ["INGESTION_BATCH_ID", "SOURCE_FILE_NAME", "INGESTED_AT_UTC"])
    projected_fields = ",\n    ".join([f"t.${index}" for index in range(1, len(data_columns) + 1)])
    stage_path = bronze_batch_stage_path(dataset, batch_id)
    return (
        f"COPY INTO {database}.{schema}.{table_name} (\n"
        f"  {load_columns}\n"
        ")\n"
        "FROM (\n"
        "  SELECT\n"
        f"    {projected_fields},\n"
        f"    '{batch_id}',\n"
        "    METADATA$FILENAME,\n"
        "    CURRENT_TIMESTAMP()\n"
        f"  FROM @{database}.{schema}.{stage_name}/{stage_path} (FILE_FORMAT => {database}.{schema}.{file_format_name}) t\n"
        ")\n"
        "ON_ERROR = 'ABORT_STATEMENT';"
    )


def _sql_file_path(batch_id: str, dataset: str) -> Path:
    out_dir = Path("warehouse/snowflake-warehouse-setup/sql/runtime")
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir / f"copy_{batch_id}_{dataset}.sql"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a dataset-specific Bronze COPY statement for a batch.")
    parser.add_argument("--batch-id", required=True, help="FraudLens batch_id from synthetic output manifest")
    parser.add_argument("--dataset", required=True, choices=DATASET_ORDER, help="Dataset name to load")
    parser.add_argument("--profile", choices=["local", "cloud"], default=None, help="Config profile override")
    parser.add_argument(
        "--write-sql",
        action="store_true",
        help="Write SQL file under warehouse/snowflake-warehouse-setup/sql/runtime",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    context = _warehouse_context(args.profile)
    sql_text = _copy_sql(
        context["database"],
        context["bronze_schema"],
        context["file_format_name"],
        context["external_stage_name"],
        args.dataset,
        args.batch_id,
    )
    if args.write_sql:
        target = _sql_file_path(args.batch_id, args.dataset)
        target.write_text(sql_text + "\n", encoding="utf-8")
        print(f"Wrote SQL file: {target}")
    print(sql_text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
