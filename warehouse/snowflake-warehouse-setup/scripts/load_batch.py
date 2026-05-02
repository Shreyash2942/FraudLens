from __future__ import annotations

import argparse
import json
from pathlib import Path

from _dataset_layout import DATASET_ORDER
from load_one_dataset import _copy_sql, _warehouse_context


def _manifest_path(batch_id: str, data_root: str) -> Path:
    return Path(data_root) / "batches" / batch_id / "control" / "manifest.json"


def _load_manifest(batch_id: str, data_root: str) -> dict:
    manifest_file = _manifest_path(batch_id, data_root)
    if not manifest_file.exists():
        raise FileNotFoundError(f"Manifest not found for batch '{batch_id}': {manifest_file}")
    with manifest_file.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Manifest content is invalid JSON object: {manifest_file}")
    return payload


def _datasets_for_batch(manifest: dict) -> list[str]:
    datasets = manifest.get("datasets", {})
    if not isinstance(datasets, dict):
        return list(DATASET_ORDER)
    selected = [name for name in DATASET_ORDER if name in datasets]
    return selected or list(DATASET_ORDER)


def _runtime_file_path(batch_id: str) -> Path:
    out_dir = Path("warehouse/snowflake-warehouse-setup/sql/runtime")
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir / f"copy_batch_{batch_id}.sql"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a full Bronze COPY SQL bundle for one FraudLens batch.")
    parser.add_argument("--batch-id", required=True, help="FraudLens batch_id")
    parser.add_argument("--profile", choices=["local", "cloud"], default=None, help="Config profile override")
    parser.add_argument("--data-root", default="data", help="Root data folder that contains batches/")
    parser.add_argument(
        "--output",
        default=None,
        help="Optional explicit output SQL file path. Defaults to sql/runtime/copy_batch_<batch_id>.sql",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = _load_manifest(args.batch_id, args.data_root)
    datasets = _datasets_for_batch(manifest)
    context = _warehouse_context(args.profile)
    sql_blocks: list[str] = []
    for dataset in datasets:
        sql_blocks.append(
            _copy_sql(
                context["database"],
                context["bronze_schema"],
                context["file_format_name"],
                context["external_stage_name"],
                dataset,
                args.batch_id,
            )
        )
    final_sql = "\n\n".join(sql_blocks).rstrip() + "\n"
    target = Path(args.output) if args.output else _runtime_file_path(args.batch_id)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(final_sql, encoding="utf-8")
    print(f"Wrote batch SQL: {target}")
    print(f"Datasets included: {len(datasets)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
