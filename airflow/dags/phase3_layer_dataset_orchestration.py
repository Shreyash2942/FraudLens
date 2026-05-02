from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path

import json
import yaml
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.task_group import TaskGroup

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from synthetic_generator.contracts import DATASET_ORDER


def _load_runtime_profile() -> tuple[str, dict]:
    profile = os.getenv("PHASE3_ENV", "local").strip().lower()
    if profile not in {"local", "cloud"}:
        profile = "local"
    config_path = REPO_ROOT / "warehouse" / "snowflake-warehouse-setup" / "config" / f"{profile}.yml"
    with config_path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle) or {}
    return profile, payload


def _layer_enabled(config: dict, layer: str) -> bool:
    layers = config.get("layers", {})
    layer_config = layers.get(layer, {})
    return bool(layer_config.get("enabled", layer == "bronze"))


def _layer_datasets(config: dict, layer: str) -> list[str]:
    layers = config.get("layers", {})
    layer_config = layers.get(layer, {})
    selected = layer_config.get("datasets", "from_contract")

    index_path = REPO_ROOT / "warehouse" / "snowflake-warehouse-setup" / "sql" / layer / "dataset_index.json"
    if index_path.exists():
        with index_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        datasets = payload.get("datasets", [])
        if isinstance(datasets, list):
            ordered = [str(entry.get("dataset")) for entry in datasets if isinstance(entry, dict) and entry.get("dataset")]
            if ordered:
                if isinstance(selected, list):
                    return [name for name in ordered if name in selected]
                return ordered

    if isinstance(selected, list):
        return [name for name in DATASET_ORDER if name in selected]
    return list(DATASET_ORDER)


def _dataset_job_command(profile: str, layer: str, dataset: str) -> str:
    script = (REPO_ROOT / "warehouse" / "snowflake-warehouse-setup" / "scripts" / "run_dataset_spark_job.py").as_posix()
    spark_submit_cmd = os.getenv("SPARK_SUBMIT_CMD", "spark-submit")
    batch_expr = "{{ dag_run.conf.get('batch_id', 'manual_batch') }}"
    return (
        f"python {script} --layer {layer} --dataset {dataset} "
        f"--batch-id {batch_expr} --profile {profile} --spark-submit-cmd {spark_submit_cmd}"
    )


def _build_layer_group(dag: DAG, config: dict, profile: str, layer: str) -> TaskGroup:
    enabled = _layer_enabled(config, layer)
    datasets = _layer_datasets(config, layer)
    with TaskGroup(group_id=f"{layer}_layer", dag=dag) as group:
        if not enabled:
            EmptyOperator(task_id=f"{layer}_disabled")
            return group
        if not datasets:
            EmptyOperator(task_id=f"{layer}_no_datasets")
            return group
        for dataset in datasets:
            BashOperator(
                task_id=f"{layer}__{dataset}",
                bash_command=_dataset_job_command(profile, layer, dataset),
                cwd=REPO_ROOT.as_posix(),
            )
    return group


profile_name, profile_config = _load_runtime_profile()

with DAG(
    dag_id="fraudlens_phase3_layer_dataset_orchestration",
    description="Phase 3 dataset-level orchestration with Bronze strict dependencies",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["fraudlens", "phase-3", "warehouse", "dataset-level"],
) as dag:
    start = EmptyOperator(task_id="start")
    bronze_done_gate = EmptyOperator(task_id="bronze_complete_gate")
    end = EmptyOperator(task_id="end")

    bronze_group = _build_layer_group(dag, profile_config, profile_name, "bronze")
    silver_group = _build_layer_group(dag, profile_config, profile_name, "silver")
    gold_group = _build_layer_group(dag, profile_config, profile_name, "gold")

    start >> bronze_group >> bronze_done_gate >> silver_group >> gold_group >> end
