from __future__ import annotations

from pathlib import Path

from _config_loader import load_profile
from _dataset_layout import (
    bronze_batch_stage_path,
    bronze_table_name,
    core_datasets,
    dimension_datasets,
    table_columns,
    table_data_columns,
)

ROOT = Path(__file__).resolve().parents[1]
SQL_ROOT = ROOT / "sql"


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


def _table_sql(database: str, schema: str, dataset: str) -> str:
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
        f"CREATE TABLE IF NOT EXISTS {database}.{schema}.{table_name} (\n"
        f"{joined}\n"
        ");\n"
    )


def _copy_sql(database: str, schema: str, file_format_name: str, stage_name: str, dataset: str) -> str:
    table_name = bronze_table_name(dataset)
    data_columns = table_data_columns(dataset)
    load_columns = ",\n  ".join(data_columns + ["INGESTION_BATCH_ID", "SOURCE_FILE_NAME", "INGESTED_AT_UTC"])
    projected_fields = ",\n    ".join([f"t.${index}" for index in range(1, len(data_columns) + 1)])
    stage_path = bronze_batch_stage_path(dataset, "$BATCH_ID")
    return (
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


def _render_table_file(database: str, schema: str, datasets: list[str], header: str) -> str:
    sections = [header.strip(), ""]
    for dataset in datasets:
        sections.append(f"-- dataset: {dataset}")
        sections.append(_table_sql(database, schema, dataset).rstrip())
        sections.append("")
    return "\n".join(sections).rstrip() + "\n"


def _render_copy_file(database: str, schema: str, file_format_name: str, stage_name: str, datasets: list[str], header: str) -> str:
    sections = [header.strip(), "", "SET BATCH_ID = '<replace_with_batch_id>';"]
    for dataset in datasets:
        sections.append("")
        sections.append(f"-- dataset: {dataset}")
        sections.append(_copy_sql(database, schema, file_format_name, stage_name, dataset).rstrip())
    return "\n".join(sections).rstrip() + "\n"


def _render_file_format_sql(database: str, schema: str, file_format_name: str) -> str:
    return (
        "-- Stage 4 (#42): standard CSV file format for FraudLens Bronze ingestion\n\n"
        f"CREATE FILE FORMAT IF NOT EXISTS {database}.{schema}.{file_format_name}\n"
        "  TYPE = CSV\n"
        "  SKIP_HEADER = 1\n"
        "  FIELD_DELIMITER = ','\n"
        "  FIELD_OPTIONALLY_ENCLOSED_BY = '\"'\n"
        "  TRIM_SPACE = TRUE\n"
        "  EMPTY_FIELD_AS_NULL = TRUE\n"
        "  NULL_IF = ('', 'NULL', 'null')\n"
        "  ERROR_ON_COLUMN_COUNT_MISMATCH = FALSE;\n"
    )


def _render_external_stage_sql(database: str, schema: str, stage_name: str, file_format_name: str) -> str:
    return (
        "-- Stage 4 (#42): MinIO S3-compatible external stage template\n"
        "-- Replace placeholder credentials/endpoints with secure values from your runtime secrets.\n\n"
        "SET MINIO_ENDPOINT = '<minio-host:port>';\n"
        "SET MINIO_BUCKET = '<bucket-name>';\n"
        "SET MINIO_PREFIX = '<prefix-root>'; -- example: fraudlens/synthetic_data/batches\n"
        "SET MINIO_ACCESS_KEY = '<access-key>';\n"
        "SET MINIO_SECRET_KEY = '<secret-key>';\n\n"
        f"CREATE STAGE IF NOT EXISTS {database}.{schema}.{stage_name}\n"
        "  URL = 's3compat://<bucket-name>/<prefix-root>/'\n"
        "  ENDPOINT = '<minio-host:port>'\n"
        "  CREDENTIALS = (AWS_KEY_ID = '<access-key>' AWS_SECRET_KEY = '<secret-key>')\n"
        f"  FILE_FORMAT = {database}.{schema}.{file_format_name};\n"
    )


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> int:
    context = _warehouse_context(None)
    database = context["database"]
    bronze_schema = context["bronze_schema"]
    file_format_name = context["file_format_name"]
    external_stage_name = context["external_stage_name"]

    ddl_dir = SQL_ROOT / "ddl"
    dml_dir = SQL_ROOT / "dml"
    staging_dir = SQL_ROOT / "staging"

    _write(
        ddl_dir / "create_bronze_tables_dimensions.sql",
        _render_table_file(
            database,
            bronze_schema,
            dimension_datasets(),
            "-- Stage 3 (#41): Bronze dimension table foundation",
        ),
    )
    _write(
        ddl_dir / "create_bronze_tables_core.sql",
        _render_table_file(
            database,
            bronze_schema,
            core_datasets(),
            "-- Stage 3 (#41): Bronze core/fraud operations table foundation",
        ),
    )

    _write(
        dml_dir / "copy_into_bronze_dimensions.sql",
        _render_copy_file(
            database,
            bronze_schema,
            file_format_name,
            external_stage_name,
            dimension_datasets(),
            "-- Stage 4 (#42): batch-based MinIO ingestion for Bronze dimensions",
        ),
    )
    _write(
        dml_dir / "copy_into_bronze_core.sql",
        _render_copy_file(
            database,
            bronze_schema,
            file_format_name,
            external_stage_name,
            core_datasets(),
            "-- Stage 4 (#42): batch-based MinIO ingestion for Bronze core/fraud datasets",
        ),
    )

    _write(staging_dir / "create_csv_file_format.sql", _render_file_format_sql(database, bronze_schema, file_format_name))
    _write(
        staging_dir / "create_minio_external_stage.sql",
        _render_external_stage_sql(database, bronze_schema, external_stage_name, file_format_name),
    )

    print("Generated Stage 3/4 SQL assets:")
    print(f"- {ddl_dir / 'create_bronze_tables_dimensions.sql'}")
    print(f"- {ddl_dir / 'create_bronze_tables_core.sql'}")
    print(f"- {dml_dir / 'copy_into_bronze_dimensions.sql'}")
    print(f"- {dml_dir / 'copy_into_bronze_core.sql'}")
    print(f"- {staging_dir / 'create_csv_file_format.sql'}")
    print(f"- {staging_dir / 'create_minio_external_stage.sql'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
