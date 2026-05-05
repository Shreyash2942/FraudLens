from __future__ import annotations

import json
import sys

from _config_loader import load_profile


def main() -> int:
    profile = sys.argv[1] if len(sys.argv) > 1 else None
    config = load_profile(profile)
    print(json.dumps(config, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
