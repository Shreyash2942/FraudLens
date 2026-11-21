"""Validate tracked Python and offline tests without private local configuration."""
from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

from scripts.ci.validate_repository import run_context, tracked_paths, validate_repository


ROOT = Path(__file__).resolve().parents[2]


def lint(root: Path, report: dict) -> bool:
    paths = [name for name in tracked_paths(root) if name.endswith(".py")]
    if not paths:
        raise ValueError("No tracked Python files found")
    result = subprocess.run(
        [sys.executable, "-m", "ruff", "check", "--config", str(root / "ruff.toml"),
         "--no-cache", "--no-fix", "--output-format", "json", "--", *paths],
        cwd=root, capture_output=True, text=True, encoding="utf-8", check=False,
    )
    if result.returncode not in (0, 1):
        raise ValueError("Ruff could not complete")
    diagnostics = json.loads(result.stdout)
    if not isinstance(diagnostics, list):
        raise ValueError("Invalid Ruff result")
    report["python_files"] = len(paths)
    report["lint_errors"] = [
        {"path": Path(item["filename"]).resolve().relative_to(root.resolve()).as_posix(),
         "rule": item["code"], "line": item["location"]["row"],
         "column": item["location"]["column"]}
        for item in diagnostics
    ]
    return result.returncode == 0 and not diagnostics


def copy_tracked_source(root: Path, destination: Path) -> None:
    for name in tracked_paths(root):
        source = root / name
        if source.is_symlink() or not source.resolve().is_relative_to(root.resolve()):
            raise ValueError("Unsafe tracked source")
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)


def run_tests(root: Path, report: dict) -> bool:
    # Isolate local .env/runtime_config and generated data, even for local reproduction.
    with tempfile.TemporaryDirectory(prefix="fraudlens-python-ci-") as directory:
        snapshot = Path(directory) / "source"
        snapshot.mkdir()
        copy_tracked_source(root, snapshot)
        xml_path = Path(directory) / "pytest.xml"
        environment = {key: value for key, value in os.environ.items()
                       if "MINIO" not in key.upper() and key.upper() not in
                       {"PYTHONPATH", "PYTHONHOME", "PYTEST_ADDOPTS", "PYTEST_PLUGINS"}}
        environment["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests", "airflow/tests", "-q",
             "--strict-config", "--strict-markers", f"--junitxml={xml_path}"],
            cwd=snapshot, env=environment, check=False,
        )
        xml = ET.parse(xml_path).getroot()
        suites = [xml] if xml.tag == "testsuite" else list(xml.findall("testsuite"))
        counts = {key: sum(int(suite.get(key, "0")) for suite in suites)
                  for key in ("tests", "failures", "errors", "skipped")}
        report["tests"] = {"workspace": "tracked_source_snapshot", "junit_counts": counts,
                           "exit_code": result.returncode}
        # Only sanitized counts leave the temporary directory; no raw JUnit/log/data upload.
        return (result.returncode == 0 and counts["tests"] > counts["skipped"]
                and counts["failures"] == counts["errors"] == 0)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=["lint", "tests"], required=True)
    parser.add_argument("--report", type=Path, default=Path(".ci-artifacts/python-validation.json"))
    args = parser.parse_args()
    report = {"schema_version": 1, "scope": "offline_python_validation", "stages": {},
              "context": run_context(ROOT),
              "dependencies": {name: importlib.metadata.version(name)
                               for name in ("pytest", "ruff", "Faker", "minio", "PyYAML")}}
    passed = False
    try:
        if args.stage == "tests":
            report = json.loads(args.report.read_text(encoding="utf-8"))
            if report.get("stages", {}).get("lint", {}).get("status") != "success":
                raise ValueError("Successful lint is required before tests")
        if not validate_repository(ROOT)["valid"]:
            raise ValueError("Tracked-file baseline must pass before running Python checks")
        passed = lint(ROOT, report) if args.stage == "lint" else run_tests(ROOT, report)
        report["stages"][args.stage] = {"status": "success" if passed else "failure"}
    except (OSError, ValueError, KeyError, ET.ParseError, subprocess.SubprocessError) as error:
        report["stages"][args.stage] = {"status": "failure", "error_type": type(error).__name__}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
