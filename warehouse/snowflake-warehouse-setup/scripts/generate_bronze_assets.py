from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    script = Path(__file__).resolve().parent / "generate_layer_assets.py"
    command = [
        sys.executable,
        str(script),
        "--layers",
        "bronze",
        "--clean",
        "--emit-spark-jobs",
    ]
    print("Delegating to generate_layer_assets.py for bronze-only generation.")
    result = subprocess.run(command, check=False)
    return int(result.returncode)


if __name__ == "__main__":
    raise SystemExit(main())
