from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_common_args(description: str) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--layer", required=True, choices=["bronze", "silver", "gold"], help="Pipeline layer")
    parser.add_argument("--dataset", required=True, help="Dataset name")
    parser.add_argument("--batch-id", required=True, help="Synthetic generation batch id")
    parser.add_argument("--profile", required=True, choices=["local", "cloud"], help="Runtime profile")
    return parser.parse_args()


@dataclass
class JobContractResult:
    status: str
    layer: str
    dataset: str
    batch_id: str
    profile: str
    row_count: int
    error_message: str
    started_at_utc: str
    finished_at_utc: str
    duration_seconds: float

    def to_json(self) -> str:
        return json.dumps(
            {
                "status": self.status,
                "layer": self.layer,
                "dataset": self.dataset,
                "batch_id": self.batch_id,
                "profile": self.profile,
                "row_count": self.row_count,
                "error_message": self.error_message,
                "started_at_utc": self.started_at_utc,
                "finished_at_utc": self.finished_at_utc,
                "duration_seconds": self.duration_seconds,
            }
        )


def run_with_contract(args: argparse.Namespace, execute_fn: Callable[[argparse.Namespace], dict[str, object]]) -> int:
    started = datetime.now(timezone.utc)
    started_at_utc = _utc_now_iso()
    try:
        output = execute_fn(args)
        status = str(output.get("status", "success"))
        row_count = int(output.get("row_count", -1))
        error_message = str(output.get("error_message", ""))
        exit_code = 0 if status in {"success", "scaffold"} else 1
    except Exception as exc:  # pragma: no cover - runtime behavior
        status = "failed"
        row_count = -1
        error_message = str(exc)
        exit_code = 1
    finished = datetime.now(timezone.utc)
    finished_at_utc = _utc_now_iso()
    duration = (finished - started).total_seconds()
    result = JobContractResult(
        status=status,
        layer=str(args.layer),
        dataset=str(args.dataset),
        batch_id=str(args.batch_id),
        profile=str(args.profile),
        row_count=row_count,
        error_message=error_message,
        started_at_utc=started_at_utc,
        finished_at_utc=finished_at_utc,
        duration_seconds=round(duration, 3),
    )
    print(result.to_json())
    return exit_code
