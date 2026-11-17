from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


def iter_jsonl(path: Path) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            payload = json.loads(stripped)
            if not isinstance(payload, dict):
                raise ValueError(f"Expected JSON object at {path}:{line_number}")
            events.append(payload)
    return events


def extract_openlineage_events(path: Path) -> list[dict[str, Any]]:
    extracted: list[dict[str, Any]] = []
    for payload in iter_jsonl(path):
        event = payload.get("openlineage_event", payload)
        if not isinstance(event, dict):
            raise ValueError(f"Lineage payload does not contain an object event: {path}")
        for required_key in ("eventType", "eventTime", "run", "job", "inputs", "outputs"):
            if required_key not in event:
                raise ValueError(f"OpenLineage event missing required key '{required_key}': {path}")
        extracted.append(event)
    return extracted


def post_event(url: str, event: dict[str, Any], *, timeout_seconds: int) -> int:
    request = urllib.request.Request(
        url,
        data=json.dumps(event).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
        return int(response.status)


def deliver_events(
    *,
    input_path: Path,
    url: str,
    dry_run: bool,
    timeout_seconds: int,
) -> dict[str, Any]:
    events = extract_openlineage_events(input_path)
    responses: list[dict[str, Any]] = []
    for index, event in enumerate(events, start=1):
        if dry_run:
            responses.append(
                {
                    "index": index,
                    "status": "dry_run",
                    "eventType": event.get("eventType"),
                    "job": (event.get("job") or {}).get("name"),
                    "runId": ((event.get("run") or {}).get("runId")),
                }
            )
            continue
        try:
            status_code = post_event(url, event, timeout_seconds=timeout_seconds)
            responses.append({"index": index, "status": "delivered", "status_code": status_code})
        except (urllib.error.URLError, TimeoutError) as exc:
            responses.append({"index": index, "status": "failed", "error": repr(exc)})
    return {
        "input": str(input_path),
        "url": url,
        "dry_run": dry_run,
        "event_count": len(events),
        "responses": responses,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Deliver OpenLineage JSONL events to Marquez/OpenLineage endpoint.")
    parser.add_argument("--input", type=Path, required=True, help="Lineage JSONL file containing OpenLineage events.")
    parser.add_argument("--url", default=os.getenv("OPENLINEAGE_URL", "http://localhost:5000/api/v1/lineage"))
    parser.add_argument("--timeout-seconds", type=int, default=10)
    parser.add_argument("--send", action="store_true", help="Post events. Omit for dry-run validation.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = deliver_events(
        input_path=args.input,
        url=args.url,
        dry_run=not args.send,
        timeout_seconds=max(args.timeout_seconds, 1),
    )
    print(json.dumps(payload, indent=2))
    if any(item.get("status") == "failed" for item in payload["responses"]):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
