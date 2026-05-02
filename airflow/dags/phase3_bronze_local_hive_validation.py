from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.task_group import TaskGroup

def _resolve_repo_root() -> Path:
    configured = os.getenv("FRAUDLENS_REPO_ROOT", "").strip()
    candidates = []
    if configured:
        candidates.append(Path(configured))
    candidates.extend(
        [
            Path("/home/datalab/fraudlens"),
            Path(__file__).resolve().parents[2],
        ]
    )
    for candidate in candidates:
        if (candidate / "synthetic_generator" / "contracts.py").exists():
            return candidate
    return Path(__file__).resolve().parents[2]


REPO_ROOT = _resolve_repo_root()
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from synthetic_generator.contracts import DATASET_ORDER


def _batch_expr() -> str:
    return "{{ dag_run.conf.get('batch_id', 'manual_batch') }}"


def _spark_submit_cmd() -> str:
    return os.getenv("BRONZE_LOCAL_SPARK_CMD", "python")


def _hive_cmd() -> str:
    return os.getenv("HIVE_CMD", "beeline")


def _hive_jdbc_url() -> str:
    return os.getenv("HIVE_JDBC_URL", "jdbc:hive2://localhost:10000/default")


def _hive_user() -> str:
    return os.getenv("HIVE_USER", "")


def _hive_password() -> str:
    return os.getenv("HIVE_PASSWORD", "")


def _hive_db() -> str:
    return os.getenv("HIVE_DATABASE", "fraudlens_local")


def _spark_check_command(dataset: str) -> str:
    script = (REPO_ROOT / "warehouse" / "snowflake-warehouse-setup" / "scripts" / "run_dataset_spark_job.py").as_posix()
    return (
        f"python {script} "
        f"--layer bronze --dataset {dataset} --batch-id {_batch_expr()} --profile local "
        f"--spark-submit-cmd {_spark_submit_cmd()}"
    )


def _hive_check_command(dataset: str) -> str:
    script = (REPO_ROOT / "warehouse" / "snowflake-warehouse-setup" / "scripts" / "run_local_hive_bronze_check.py").as_posix()
    user_arg = f"--hive-user {_hive_user()}" if _hive_user() else ""
    pass_arg = f"--hive-password {_hive_password()}" if _hive_password() else ""
    return (
        f"python {script} "
        f"--dataset {dataset} --batch-id {_batch_expr()} --data-root data "
        f"--database-name {_hive_db()} --hive-cmd {_hive_cmd()} --hive-jdbc-url {_hive_jdbc_url()} "
        f"{user_arg} {pass_arg} --execute"
    )


def _precheck_command() -> str:
    expected = len(DATASET_ORDER)
    return f"""
python - <<'PY'
from pathlib import Path
import json
expected = {expected}
ddl = len(list(Path('.').glob("warehouse/snowflake-warehouse-setup/sql/bronze/ddl/bronze__*.sql")))
dml = len(list(Path('.').glob("warehouse/snowflake-warehouse-setup/sql/bronze/dml/bronze__*.sql")))
assert ddl == expected, f"Expected {{expected}} bronze DDL files, got {{ddl}}"
assert dml == expected, f"Expected {{expected}} bronze DML files, got {{dml}}"
print(json.dumps({{"status": "ok", "bronze_ddl_files": ddl, "bronze_dml_files": dml}}))
PY
""".strip()


with DAG(
    dag_id="fraudlens_phase3_bronze_local_hive_validation",
    description="Local Bronze validation DAG for Spark contract jobs and Hive DDL/DML checks",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["fraudlens", "phase-3", "bronze", "local", "hive", "spark"],
) as dag:
    start = EmptyOperator(task_id="start")
    precheck = BashOperator(task_id="precheck_bronze_assets", bash_command=_precheck_command(), cwd=REPO_ROOT.as_posix())

    with TaskGroup(group_id="bronze_local_validation") as bronze_local_validation:
        for dataset_name in DATASET_ORDER:
            spark_task = BashOperator(
                task_id=f"spark_contract__{dataset_name}",
                bash_command=_spark_check_command(dataset_name),
                cwd=REPO_ROOT.as_posix(),
            )
            hive_task = BashOperator(
                task_id=f"hive_ddl_dml__{dataset_name}",
                bash_command=_hive_check_command(dataset_name),
                cwd=REPO_ROOT.as_posix(),
            )
            spark_task >> hive_task

    end = EmptyOperator(task_id="end")
    start >> precheck >> bronze_local_validation >> end
