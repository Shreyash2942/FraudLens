from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path

from _dataset_layout import DATASET_ORDER, table_data_columns


def _infer_hive_type(column_name: str) -> str:
    lowered = column_name.lower()
    if lowered.startswith("is_"):
        return "BOOLEAN"
    if lowered.endswith("_amount"):
        return "DECIMAL(18,2)"
    if lowered.endswith("_minutes"):
        return "INT"
    if lowered.endswith("_year") or lowered.endswith("_quarter") or lowered.endswith("_month") or lowered.endswith("_week"):
        return "INT"
    if lowered.endswith("_date"):
        return "DATE"
    if lowered.endswith("_at"):
        return "TIMESTAMP"
    if lowered.startswith("elapsed_"):
        return "DECIMAL(18,2)"
    return "STRING"


def _hive_cast_expr(column_name: str, stage_alias: str = "s") -> str:
    hive_type = _infer_hive_type(column_name)
    source = f"{stage_alias}.{column_name}"
    if hive_type == "BOOLEAN":
        return (
            f"CASE "
            f"WHEN lower({source}) IN ('true','1','t','yes','y') THEN true "
            f"WHEN lower({source}) IN ('false','0','f','no','n') THEN false "
            f"ELSE NULL END"
        )
    if hive_type in {"DATE", "TIMESTAMP", "INT"} or hive_type.startswith("DECIMAL"):
        return f"CAST({source} AS {hive_type})"
    return source


def _build_sql(dataset: str, batch_id: str, stage_path: str, database_name: str) -> tuple[str, str, str]:
    dataset_cols = [col.lower() for col in table_data_columns(dataset)]
    stg_table = f"stg_bronze_{dataset}"
    tgt_table = f"bronze_{dataset}"

    stg_cols = ",\n  ".join([f"{col} STRING" for col in dataset_cols])
    tgt_cols = ",\n  ".join([f"{col} {_infer_hive_type(col)}" for col in dataset_cols] + [
        "ingestion_batch_id STRING",
        "source_file_name STRING",
        "ingested_at_utc TIMESTAMP",
    ])

    ddl_sql = f"""-- Local Hive Bronze DDL check for dataset: {dataset}
CREATE DATABASE IF NOT EXISTS {database_name};
USE {database_name};

DROP TABLE IF EXISTS {stg_table};
CREATE EXTERNAL TABLE IF NOT EXISTS {stg_table} (
  {stg_cols}
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
  "separatorChar" = ",",
  "quoteChar" = "\\\"",
  "escapeChar" = "\\\\"
)
STORED AS TEXTFILE
LOCATION '{stage_path}';

CREATE TABLE IF NOT EXISTS {tgt_table} (
  {tgt_cols}
)
STORED AS PARQUET;
"""

    select_list = ",\n  ".join([f"{_hive_cast_expr(col)} AS {col}" for col in dataset_cols] + [
        f"'{batch_id}' AS ingestion_batch_id",
        f"'{dataset}.csv' AS source_file_name",
        "CURRENT_TIMESTAMP AS ingested_at_utc",
    ])

    dml_sql = f"""-- Local Hive Bronze DML check for dataset: {dataset}
USE {database_name};

INSERT OVERWRITE TABLE {tgt_table}
SELECT
  {select_list}
FROM {stg_table} s;
"""

    verify_sql = f"""USE {database_name};
SELECT '{dataset}' AS dataset_name, COUNT(*) AS row_count
FROM {tgt_table}
WHERE ingestion_batch_id = '{batch_id}';
"""
    return ddl_sql, dml_sql, verify_sql


def _run_beeline(sql_file: Path, hive_cmd: str, jdbc_url: str, username: str, password: str) -> None:
    command = [hive_cmd, "-u", jdbc_url]
    if username:
        command.extend(["-n", username])
    if password:
        command.extend(["-p", password])
    command.extend(["-f", str(sql_file)])
    subprocess.run(command, check=True)


def _runtime_sql_dir(batch_id: str, dataset: str) -> Path:
    return Path("warehouse/snowflake-warehouse-setup/sql/bronze/hive/runtime") / batch_id / dataset


def _prepare_stage_folder(dataset: str, batch_id: str, data_root: str) -> tuple[Path, Path]:
    source_file = Path(data_root) / "batches" / batch_id / "landing" / "csv" / f"{dataset}.csv"
    if not source_file.exists():
        raise FileNotFoundError(f"Dataset CSV not found for batch '{batch_id}': {source_file}")
    stage_dir = Path(data_root) / "batches" / batch_id / "landing" / "hive_stage" / dataset
    stage_dir.mkdir(parents=True, exist_ok=True)
    stage_file = stage_dir / "part-00000.csv"
    shutil.copy2(source_file, stage_file)
    return source_file, stage_dir


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run local Hive Bronze DDL/DML check for one dataset.")
    parser.add_argument("--dataset", required=True, choices=DATASET_ORDER, help="Dataset to validate in Hive")
    parser.add_argument("--batch-id", required=True, help="Batch id under data/batches/")
    parser.add_argument("--data-root", default="data", help="Root data folder containing batches/")
    parser.add_argument("--database-name", default="fraudlens_local", help="Local Hive database name")
    parser.add_argument("--hive-cmd", default="beeline", help="Hive CLI command (beeline/hive)")
    parser.add_argument("--hive-jdbc-url", default="jdbc:hive2://localhost:10000/default", help="Hive JDBC URL")
    parser.add_argument("--hive-user", default="", help="Hive username")
    parser.add_argument("--hive-password", default="", help="Hive password")
    parser.add_argument("--execute", action="store_true", help="Execute generated SQL in Hive")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_file, stage_dir = _prepare_stage_folder(args.dataset, args.batch_id, args.data_root)
    stage_path = stage_dir.resolve().as_posix()
    ddl_sql, dml_sql, verify_sql = _build_sql(args.dataset, args.batch_id, stage_path, args.database_name)

    sql_dir = _runtime_sql_dir(args.batch_id, args.dataset)
    sql_dir.mkdir(parents=True, exist_ok=True)
    ddl_file = sql_dir / f"bronze__{args.dataset}__ddl.sql"
    dml_file = sql_dir / f"bronze__{args.dataset}__dml.sql"
    verify_file = sql_dir / f"bronze__{args.dataset}__verify.sql"
    ddl_file.write_text(ddl_sql, encoding="utf-8")
    dml_file.write_text(dml_sql, encoding="utf-8")
    verify_file.write_text(verify_sql, encoding="utf-8")

    executed = False
    if args.execute:
        _run_beeline(ddl_file, args.hive_cmd, args.hive_jdbc_url, args.hive_user, args.hive_password)
        _run_beeline(dml_file, args.hive_cmd, args.hive_jdbc_url, args.hive_user, args.hive_password)
        _run_beeline(verify_file, args.hive_cmd, args.hive_jdbc_url, args.hive_user, args.hive_password)
        executed = True

    result = {
        "status": "ok",
        "dataset": args.dataset,
        "batch_id": args.batch_id,
        "source_csv": str(source_file),
        "hive_stage_path": stage_path,
        "ddl_sql": str(ddl_file),
        "dml_sql": str(dml_file),
        "verify_sql": str(verify_file),
        "executed_in_hive": executed,
        "hive_cmd": args.hive_cmd,
        "hive_jdbc_url": args.hive_jdbc_url,
    }
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
