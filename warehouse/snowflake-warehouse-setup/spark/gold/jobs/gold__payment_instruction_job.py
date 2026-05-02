from __future__ import annotations

import sys
from pathlib import Path

COMMON_PATH = Path(__file__).resolve().parents[2] / "common"
if str(COMMON_PATH) not in sys.path:
    sys.path.insert(0, str(COMMON_PATH))

from dataset_job_contract import parse_common_args, run_with_contract

EXPECTED_LAYER = "gold"
EXPECTED_DATASET = "payment_instruction"


def execute(args):
    if args.layer != EXPECTED_LAYER:
        return {"status": "failed", "row_count": -1, "error_message": f"Layer mismatch: {args.layer} != {EXPECTED_LAYER}"}
    if args.dataset != EXPECTED_DATASET:
        return {"status": "failed", "row_count": -1, "error_message": f"Dataset mismatch: {args.dataset} != {EXPECTED_DATASET}"}
    return {
        "status": "scaffold",
        "row_count": 0,
        "error_message": "",
    }


def main() -> int:
    args = parse_common_args(description="FraudLens gold dataset job: payment_instruction")
    return run_with_contract(args, execute)


if __name__ == "__main__":
    raise SystemExit(main())
