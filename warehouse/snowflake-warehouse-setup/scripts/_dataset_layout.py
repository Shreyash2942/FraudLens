from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from synthetic_generator.contracts import CSV_FIELD_ORDER, DATASET_ORDER

DIMENSION_DATASETS = {
    "reference_data_catalog",
    "calendar_day",
    "region",
    "branch_territory",
    "branch_location",
    "business_unit",
    "analyst_team",
}


def core_datasets() -> list[str]:
    return [name for name in DATASET_ORDER if name not in DIMENSION_DATASETS]


def dimension_datasets() -> list[str]:
    return [name for name in DATASET_ORDER if name in DIMENSION_DATASETS]


def bronze_table_name(dataset: str) -> str:
    return f"BRONZE_{dataset.upper()}"


def silver_table_name(dataset: str) -> str:
    return f"SILVER_{dataset.upper()}"


def gold_table_name(dataset: str) -> str:
    return f"GOLD_{dataset.upper()}"


def bronze_file_name(dataset: str) -> str:
    return f"{dataset}.csv"


def bronze_batch_stage_path(dataset: str, batch_id: str) -> str:
    return f"{batch_id}/raw_zone/csv/{bronze_file_name(dataset)}"


def layer_sql_file_name(layer: str, dataset: str) -> str:
    return f"{layer.lower()}__{dataset}.sql"


def layer_spark_job_file_name(layer: str, dataset: str) -> str:
    return f"{layer.lower()}__{dataset}_job.py"


def infer_snowflake_type(column_name: str) -> str:
    lowered = column_name.lower()
    if lowered.startswith("is_"):
        return "BOOLEAN"
    if lowered.endswith("_amount"):
        return "NUMBER(18,2)"
    if lowered.endswith("_minutes"):
        return "NUMBER(9,0)"
    if lowered.endswith("_year") or lowered.endswith("_quarter") or lowered.endswith("_month") or lowered.endswith("_week"):
        return "NUMBER(9,0)"
    if lowered.endswith("_date"):
        return "DATE"
    if lowered.endswith("_at"):
        return "TIMESTAMP_NTZ"
    if lowered.startswith("elapsed_"):
        return "NUMBER(18,2)"
    return "VARCHAR"


def table_columns(dataset: str) -> list[tuple[str, str]]:
    cols = CSV_FIELD_ORDER[dataset]
    return [(col.upper(), infer_snowflake_type(col)) for col in cols]


def csv_field_count(dataset: str) -> int:
    return len(CSV_FIELD_ORDER[dataset])


def table_data_columns(dataset: str) -> list[str]:
    return [column.upper() for column in CSV_FIELD_ORDER[dataset]]
