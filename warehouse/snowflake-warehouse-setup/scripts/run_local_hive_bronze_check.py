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


def _build_sql(dataset: str, batch_id: str, stage_path: str, database_name: str) -> tuple[str, str, str, str]:
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

SET hive.execution.engine=mr;
SET mapreduce.framework.name=local;
SET hive.exec.mode.local.auto=true;
SET hive.exec.mode.local.auto.inputbytes.max=134217728;

INSERT OVERWRITE TABLE {tgt_table}
SELECT
  {select_list}
FROM {stg_table} s;
"""

    explain_sql = f"""-- Local Hive Bronze DML EXPLAIN check for dataset: {dataset}
USE {database_name};

SET hive.execution.engine=mr;
SET mapreduce.framework.name=local;
SET hive.exec.mode.local.auto=true;
SET hive.exec.mode.local.auto.inputbytes.max=134217728;

EXPLAIN
INSERT OVERWRITE TABLE {tgt_table}
SELECT
  {select_list}
FROM {stg_table} s;
"""

    verify_sql = f"""USE {database_name};
SET hive.fetch.task.conversion=more;
SELECT '{dataset}' AS dataset_name, ingestion_batch_id
FROM {tgt_table}
WHERE ingestion_batch_id = '{batch_id}'
LIMIT 1;
"""
    return ddl_sql, dml_sql, explain_sql, verify_sql


def _run_beeline(sql_file: Path, hive_cmd: str, jdbc_url: str, username: str, password: str) -> None:
    command = [hive_cmd, "-u", jdbc_url]
    if username:
        command.extend(["-n", username])
    if password:
        command.extend(["-p", password])
    command.extend(["-f", str(sql_file)])
    subprocess.run(command, check=True)


def _runtime_sql_dir(batch_id: str, dataset: str) -> Path:
    return Path("warehouse/snowflake-warehouse-setup/sql/bronze/hive/runtime_sql") / batch_id / dataset


def _ensure_runtime_dir(path: Path) -> None:
    for node in reversed(path.parents):
        if str(node) in {"", "."}:
            continue
        if node.exists() and not node.is_dir():
            node.unlink()
        node.mkdir(exist_ok=True)
    if path.exists() and not path.is_dir():
        path.unlink()
    path.mkdir(exist_ok=True)


def _resolve_batch_id(raw_batch_id: str, data_root: str) -> str:
    value = (raw_batch_id or "").strip()
    if value and value.lower() not in {"latest", "auto"}:
        return value
    batches_dir = Path(data_root) / "batches"
    if not batches_dir.exists():
        raise FileNotFoundError(f"Batches directory not found: {batches_dir}")
    candidates = [path for path in batches_dir.iterdir() if path.is_dir()]
    if not candidates:
        raise FileNotFoundError(f"No batch directories found under: {batches_dir}")
    latest = sorted(candidates, key=lambda p: p.stat().st_mtime, reverse=True)[0]
    return latest.name


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
    parser.add_argument(
        "--batch-id",
        required=True,
        help="Batch id under data/batches/ (or 'latest' to auto-pick newest batch)",
    )
    parser.add_argument("--data-root", default="data", help="Root data folder containing batches/")
    parser.add_argument("--database-name", default="fraudlens_local", help="Local Hive database name")
    parser.add_argument("--hive-cmd", default="beeline", help="Hive CLI command (beeline/hive)")
    parser.add_argument("--hive-jdbc-url", default="jdbc:hive2://localhost:10000/default", help="Hive JDBC URL")
    parser.add_argument("--hive-user", default="", help="Hive username")
    parser.add_argument("--hive-password", default="", help="Hive password")
    parser.add_argument("--execute", action="store_true", help="Execute generated SQL in Hive")
    parser.add_argument(
        "--dml-mode",
        choices=["explain", "execute"],
        default="explain",
        help="DML validation mode when --execute is set",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    resolved_batch_id = _resolve_batch_id(args.batch_id, args.data_root)
    source_file, stage_dir = _prepare_stage_folder(args.dataset, resolved_batch_id, args.data_root)
    stage_path = stage_dir.resolve().as_posix()
    ddl_sql, dml_sql, explain_sql, verify_sql = _build_sql(args.dataset, resolved_batch_id, stage_path, args.database_name)

    sql_dir = _runtime_sql_dir(resolved_batch_id, args.dataset)
    _ensure_runtime_dir(sql_dir)
    ddl_file = sql_dir / f"bronze__{args.dataset}__ddl.sql"
    dml_file = sql_dir / f"bronze__{args.dataset}__dml.sql"
    explain_file = sql_dir / f"bronze__{args.dataset}__dml_explain.sql"
    verify_file = sql_dir / f"bronze__{args.dataset}__verify.sql"
    ddl_file.write_text(ddl_sql, encoding="utf-8")
    dml_file.write_text(dml_sql, encoding="utf-8")
    explain_file.write_text(explain_sql, encoding="utf-8")
    verify_file.write_text(verify_sql, encoding="utf-8")

    executed = False
    if args.execute:
        _run_beeline(ddl_file, args.hive_cmd, args.hive_jdbc_url, args.hive_user, args.hive_password)
        if args.dml_mode == "execute":
            _run_beeline(dml_file, args.hive_cmd, args.hive_jdbc_url, args.hive_user, args.hive_password)
            _run_beeline(verify_file, args.hive_cmd, args.hive_jdbc_url, args.hive_user, args.hive_password)
        else:
            _run_beeline(explain_file, args.hive_cmd, args.hive_jdbc_url, args.hive_user, args.hive_password)
        executed = True

    result = {
        "status": "ok",
        "dataset": args.dataset,
        "batch_id": resolved_batch_id,
        "source_csv": str(source_file),
        "hive_stage_path": stage_path,
        "ddl_sql": str(ddl_file),
        "dml_sql": str(dml_file),
        "dml_explain_sql": str(explain_file),
        "verify_sql": str(verify_file),
        "executed_in_hive": executed,
        "dml_mode": args.dml_mode,
        "hive_cmd": args.hive_cmd,
        "hive_jdbc_url": args.hive_jdbc_url,
    }
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
