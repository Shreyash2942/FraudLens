from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from _dataset_layout import DATASET_ORDER

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_dataset_spark_job.py"
OUTPUT_DIR = ROOT / "sql" / "runtime" / "performance"


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _utc_now_iso() -> str:
    return _utc_now().strftime("%Y-%m-%dT%H:%M:%SZ")


def _latest_batch_id(data_root: str) -> str:
    batches_dir = Path(data_root) / "batches"
    if not batches_dir.exists():
        raise FileNotFoundError(f"Batches folder not found: {batches_dir}")
    candidates = [item.name for item in batches_dir.iterdir() if item.is_dir()]
    if not candidates:
        raise FileNotFoundError(f"No batch directories found under: {batches_dir}")
    return sorted(candidates)[-1]


def _resolve_batch_id(batch_id: str, data_root: str) -> str:
    selected = batch_id.strip()
    if selected.lower() != "latest":
        return selected
    return _latest_batch_id(data_root)


def _datasets_arg(datasets_raw: str | None) -> list[str]:
    if not datasets_raw:
        return list(DATASET_ORDER)
    requested = [token.strip() for token in datasets_raw.split(",") if token.strip()]
    invalid = [name for name in requested if name not in DATASET_ORDER]
    if invalid:
        choices = ", ".join(DATASET_ORDER)
        raise ValueError(f"Invalid dataset(s): {', '.join(invalid)}. Allowed: {choices}")
    return requested


def _runtime_output_paths(batch_id: str) -> tuple[Path, Path]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = _utc_now().strftime("%Y%m%d_%H%M%S")
    base = OUTPUT_DIR / f"benchmark_{batch_id}_{stamp}"
    return (base.with_suffix(".json"), base.with_suffix(".md"))


def _extract_contract(stdout: str) -> dict[str, Any]:
    for line in reversed(stdout.splitlines()):
        candidate = line.strip()
        if not candidate.startswith("{") or not candidate.endswith("}"):
            continue
        try:
            payload = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict) and "status" in payload and "dataset" in payload:
            return payload
    return {"status": "failed", "dataset": "", "error_message": "No job contract JSON emitted"}


def _execute_dataset(
    layer: str,
    dataset: str,
    batch_id: str,
    profile: str,
    spark_submit_cmd: str,
    python_cmd: str,
) -> dict[str, Any]:
    command = [
        python_cmd,
        str(RUNNER),
        "--layer",
        layer,
        "--dataset",
        dataset,
        "--batch-id",
        batch_id,
        "--profile",
        profile,
        "--spark-submit-cmd",
        spark_submit_cmd,
    ]
    started = _utc_now()
    start_monotonic = time.monotonic()
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    wall_clock_seconds = round(time.monotonic() - start_monotonic, 3)
    finished = _utc_now()

    contract = _extract_contract(completed.stdout)
    duration_contract = contract.get("duration_seconds")
    try:
        contract_duration_seconds = round(float(duration_contract), 3)
    except (TypeError, ValueError):
        contract_duration_seconds = -1.0

    return {
        "layer": layer,
        "dataset": dataset,
        "batch_id": batch_id,
        "profile": profile,
        "status": str(contract.get("status", "failed")),
        "row_count": int(contract.get("row_count", -1)),
        "error_message": str(contract.get("error_message", "")),
        "started_at_utc": started.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "finished_at_utc": finished.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "duration_seconds_contract": contract_duration_seconds,
        "duration_seconds_wall_clock": wall_clock_seconds,
        "exit_code": int(completed.returncode),
    }


def _build_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(records)
    succeeded = sum(1 for item in records if item.get("status") in {"success", "scaffold"})
    failed = total - succeeded
    total_rows = sum(int(item.get("row_count", 0)) for item in records if int(item.get("row_count", 0)) > 0)
    total_seconds = round(sum(float(item.get("duration_seconds_wall_clock", 0.0)) for item in records), 3)
    throughput = round(total_rows / total_seconds, 3) if total_rows > 0 and total_seconds > 0 else 0.0
    return {
        "total_runs": total,
        "succeeded_runs": succeeded,
        "failed_runs": failed,
        "total_rows_loaded": total_rows,
        "total_wall_clock_seconds": total_seconds,
        "rows_per_second_wall_clock": throughput,
    }


def _write_markdown_report(target: Path, payload: dict[str, Any]) -> None:
    lines: list[str] = []
    lines.append("# Bronze Load Benchmark Report")
    lines.append("")
    lines.append(f"- generated_at_utc: `{payload['generated_at_utc']}`")
    lines.append(f"- batch_id: `{payload['batch_id']}`")
    lines.append(f"- profile: `{payload['profile']}`")
    lines.append(f"- layer: `{payload['layer']}`")
    lines.append(f"- runs_per_dataset: `{payload['runs_per_dataset']}`")
    lines.append(f"- datasets: `{len(payload['datasets'])}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    summary = payload["summary"]
    lines.append(f"- total_runs: `{summary['total_runs']}`")
    lines.append(f"- succeeded_runs: `{summary['succeeded_runs']}`")
    lines.append(f"- failed_runs: `{summary['failed_runs']}`")
    lines.append(f"- total_rows_loaded: `{summary['total_rows_loaded']}`")
    lines.append(f"- total_wall_clock_seconds: `{summary['total_wall_clock_seconds']}`")
    lines.append(f"- rows_per_second_wall_clock: `{summary['rows_per_second_wall_clock']}`")
    lines.append("")
    lines.append("## Dataset Runs")
    lines.append("")
    lines.append("| dataset | run_index | status | row_count | contract_s | wall_clock_s | exit_code |")
    lines.append("|---|---:|---|---:|---:|---:|---:|")
    for item in payload["runs"]:
        lines.append(
            f"| {item['dataset']} | {item['run_index']} | {item['status']} | {item['row_count']} | "
            f"{item['duration_seconds_contract']} | {item['duration_seconds_wall_clock']} | {item['exit_code']} |"
        )
    lines.append("")
    target.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Capture baseline Bronze load performance by running per-dataset Spark job contracts."
    )
    parser.add_argument("--batch-id", required=True, help="Batch id to benchmark, or 'latest'")
    parser.add_argument("--profile", choices=["local", "cloud"], default="local", help="Runtime profile")
    parser.add_argument("--layer", choices=["bronze"], default="bronze", help="Target layer (Phase 3 baseline is bronze)")
    parser.add_argument(
        "--datasets",
        default=None,
        help="Optional comma-separated subset of datasets. Defaults to all contract datasets.",
    )
    parser.add_argument("--runs", type=int, default=1, help="Number of repeat runs per dataset")
    parser.add_argument(
        "--spark-submit-cmd",
        default=os.getenv("SPARK_SUBMIT_CMD", "spark-submit"),
        help="Command forwarded to run_dataset_spark_job.py",
    )
    parser.add_argument(
        "--python-cmd",
        default="py",
        help="Python command used to execute run_dataset_spark_job.py",
    )
    parser.add_argument("--data-root", default="data", help="Root directory that contains batches/")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.runs < 1:
        raise ValueError("--runs must be >= 1")

    batch_id = _resolve_batch_id(args.batch_id, args.data_root)
    datasets = _datasets_arg(args.datasets)
    runs: list[dict[str, Any]] = []

    for run_index in range(1, args.runs + 1):
        for dataset in datasets:
            result = _execute_dataset(
                layer=args.layer,
                dataset=dataset,
                batch_id=batch_id,
                profile=args.profile,
                spark_submit_cmd=args.spark_submit_cmd,
                python_cmd=args.python_cmd,
            )
            result["run_index"] = run_index
            runs.append(result)
            print(
                f"[run {run_index}] dataset={dataset} status={result['status']} "
                f"rows={result['row_count']} wall_s={result['duration_seconds_wall_clock']}"
            )

    summary = _build_summary(runs)
    payload = {
        "generated_at_utc": _utc_now_iso(),
        "batch_id": batch_id,
        "profile": args.profile,
        "layer": args.layer,
        "runs_per_dataset": args.runs,
        "datasets": datasets,
        "spark_submit_cmd": args.spark_submit_cmd,
        "summary": summary,
        "runs": runs,
    }

    json_path, md_path = _runtime_output_paths(batch_id)
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    _write_markdown_report(md_path, payload)

    print(f"Wrote benchmark JSON: {json_path}")
    print(f"Wrote benchmark markdown: {md_path}")
    print(
        "Summary:",
        json.dumps(
            {
                "total_runs": summary["total_runs"],
                "succeeded_runs": summary["succeeded_runs"],
                "failed_runs": summary["failed_runs"],
                "total_wall_clock_seconds": summary["total_wall_clock_seconds"],
            }
        ),
    )
    return 0 if summary["failed_runs"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
