from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from _dataset_layout import DATASET_ORDER, layer_spark_job_file_name

ROOT = Path(__file__).resolve().parents[1]
SPARK_ROOT = ROOT / "spark"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run one layer/dataset Spark job with the standard job contract.")
    parser.add_argument("--layer", required=True, choices=["bronze", "silver", "gold"], help="Layer to execute")
    parser.add_argument("--dataset", required=True, choices=DATASET_ORDER, help="Dataset to execute")
    parser.add_argument("--batch-id", required=True, help="Batch id from synthetic generation")
    parser.add_argument("--profile", required=True, choices=["local", "cloud"], help="Runtime profile")
    parser.add_argument("--spark-submit-cmd", default="spark-submit", help="Spark submit command")
    return parser.parse_args()


def _job_path(layer: str, dataset: str) -> Path:
    return SPARK_ROOT / layer / "jobs" / layer_spark_job_file_name(layer, dataset)


def main() -> int:
    args = parse_args()
    target = _job_path(args.layer, args.dataset)
    if not target.exists():
        raise FileNotFoundError(f"Spark job file not found: {target}")

    command = [
        args.spark_submit_cmd,
        str(target),
        "--layer",
        args.layer,
        "--dataset",
        args.dataset,
        "--batch-id",
        args.batch_id,
        "--profile",
        args.profile,
    ]
    print("Executing:", " ".join(command))
    completed = subprocess.run(command, check=False)
    return int(completed.returncode)


if __name__ == "__main__":
    raise SystemExit(main())
