from __future__ import annotations

import csv
import json
from pathlib import Path

from .contracts import CSV_FIELD_ORDER, DATASET_ORDER
from .progress import ProgressReporter
from .utils import ensure_directory


def write_run_outputs(
    run_dir: Path, datasets: dict[str, list[dict]], progress: ProgressReporter | None = None
) -> dict[str, str]:
    csv_dir = run_dir / "landing" / "csv"
    ensure_directory(csv_dir)
    output_paths: dict[str, str] = {}
    total = len(DATASET_ORDER)
    for index, dataset_name in enumerate(DATASET_ORDER, start=1):
        rows = datasets.get(dataset_name, [])
        file_path = csv_dir / f"{dataset_name}.csv"
        with file_path.open("w", newline="", encoding="utf-8") as handle:
            fieldnames = CSV_FIELD_ORDER[dataset_name]
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow({field: row.get(field, "") for field in fieldnames})
        output_paths[dataset_name] = str(file_path)
        if progress:
            progress.tick(
                key="csv_export",
                current=index,
                total=total,
                label="Writing dataset CSV files",
                every=1,
            )
    return output_paths


def write_json(path: Path, payload: dict) -> None:
    ensure_directory(path.parent)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
