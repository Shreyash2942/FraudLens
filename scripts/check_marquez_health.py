from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_url(base_url: str, path: str) -> str:
    return base_url.rstrip("/") + "/" + path.lstrip("/")


def check_marquez_health(*, base_url: str, health_path: str, timeout_seconds: int) -> dict[str, Any]:
    url = normalize_url(base_url, health_path)
    started = time.perf_counter()
    payload: dict[str, Any] = {
        "checked_at_utc": utc_now_iso(),
        "base_url": base_url,
        "health_url": url,
        "status": "unknown",
    }
    try:
        with urllib.request.urlopen(url, timeout=timeout_seconds) as response:
            payload["status_code"] = int(response.status)
            payload["status"] = "healthy" if 200 <= int(response.status) < 500 else "unhealthy"
    except urllib.error.URLError as exc:
        payload["status"] = "unreachable"
        payload["error"] = repr(exc)
    finally:
        payload["response_time_seconds"] = round(time.perf_counter() - started, 3)
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check Marquez API reachability for FraudLens lineage validation.")
    parser.add_argument("--base-url", default=os.getenv("MARQUEZ_BASE_URL", "http://localhost:3003"))
    parser.add_argument("--health-path", default=os.getenv("MARQUEZ_HEALTH_PATH", "/api/v1/namespaces"))
    parser.add_argument("--timeout-seconds", type=int, default=5)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = check_marquez_health(
        base_url=args.base_url,
        health_path=args.health_path,
        timeout_seconds=max(args.timeout_seconds, 1),
    )
    print(json.dumps(payload, indent=2))
    return 0 if payload["status"] == "healthy" else 1


if __name__ == "__main__":
    raise SystemExit(main())
