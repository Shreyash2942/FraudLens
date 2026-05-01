from __future__ import annotations

import socket
from urllib.parse import urlparse

from _config_loader import load_profile, resolve_secret


def _check_host_port(host: str, port: int, timeout: float = 3.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _parse_endpoint(endpoint: str) -> tuple[str, int]:
    parsed = urlparse(endpoint)
    host = parsed.hostname or "localhost"
    if parsed.port:
        return host, parsed.port
    if parsed.scheme == "https":
        return host, 443
    return host, 80


def _check_local(config: dict) -> list[tuple[str, bool, str]]:
    checks: list[tuple[str, bool, str]] = []
    trino_host = resolve_secret("TRINO_HOST", "localhost")
    trino_port = int(resolve_secret("TRINO_PORT", "8085"))
    checks.append(("trino", _check_host_port(trino_host, trino_port), f"{trino_host}:{trino_port}"))

    minio_endpoint = resolve_secret("MINIO_ENDPOINT", config.get("object_storage", {}).get("endpoint", "http://localhost:9009"))
    host, port = _parse_endpoint(minio_endpoint)
    checks.append(("minio", _check_host_port(host, port), f"{host}:{port}"))
    return checks


def _check_cloud() -> list[tuple[str, bool, str]]:
    checks: list[tuple[str, bool, str]] = []
    required = [
        "SNOWFLAKE_ACCOUNT",
        "SNOWFLAKE_USER",
        "SNOWFLAKE_PASSWORD",
        "SNOWFLAKE_ROLE",
        "SNOWFLAKE_WAREHOUSE",
        "SNOWFLAKE_DATABASE",
    ]
    for key in required:
        present = bool(resolve_secret(key))
        checks.append((key, present, "set" if present else "missing"))
    return checks


def main() -> int:
    config = load_profile()
    env_name = str(config.get("environment", "local")).lower()
    checks = _check_cloud() if env_name == "cloud" else _check_local(config)

    failed = 0
    for name, ok, detail in checks:
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {name}: {detail}")
        if not ok:
            failed += 1
    print(f"Connectivity summary | environment={env_name} | passed={len(checks)-failed} | failed={failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
