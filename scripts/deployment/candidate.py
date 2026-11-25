"""Immutable source bundles; PR bundles are previews, never promotion evidence."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import subprocess
import tarfile
from pathlib import Path, PurePosixPath

from scripts.ci.validate_repository import validate_repository


ROOT = Path(__file__).resolve().parents[2]
REPOSITORY = "Shreyash2942/FraudLens"
SHA = re.compile(r"^[0-9a-f]{40}$")
DIGEST = re.compile(r"^[0-9a-f]{64}$")
MAX_BYTES = 100 * 1024 * 1024


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build(root: Path, output: Path, context: dict[str, str]) -> dict:
    if not validate_repository(root, required_paths=())["valid"]:
        raise ValueError("Tracked source failed baseline validation")
    subprocess.run(["git", "diff", "--quiet", "HEAD"], cwd=root, check=True)
    source_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root).decode().strip()
    if not SHA.fullmatch(source_sha) or context.get("GITHUB_REPOSITORY", REPOSITORY) != REPOSITORY:
        raise ValueError("Invalid candidate identity")
    files = {}
    entries = subprocess.check_output(["git", "ls-tree", "-rz", "--full-tree", "HEAD"], cwd=root)
    for entry in entries.split(b"\0"):
        if not entry:
            continue
        header, raw_name = entry.split(b"\t", 1)
        mode, kind, blob = header.decode().split()
        name = raw_name.decode("utf-8")
        if mode not in ("100644", "100755") or kind != "blob":
            raise ValueError("Only regular source files may enter a candidate")
        files[name] = (subprocess.check_output(["git", "cat-file", "blob", blob], cwd=root), mode)
    if not files or sum(len(data) for data, _ in files.values()) > MAX_BYTES:
        raise ValueError("Candidate inventory is empty or too large")
    manifest = {"schema_version": 1, "repository": REPOSITORY, "source_sha": source_sha,
                "ci_run_id": context.get("GITHUB_RUN_ID", "0"),
                "ci_run_attempt": context.get("GITHUB_RUN_ATTEMPT", "1"),
                "origin_main_push": context.get("GITHUB_EVENT_NAME") == "push"
                and context.get("GITHUB_REF") == "refs/heads/main",
                "files": {name: {"sha256": sha256(data), "mode": mode} for name, (data, mode) in sorted(files.items())}}
    output.mkdir(parents=True, exist_ok=True)
    bundle = output / "candidate.tar"
    with tarfile.open(bundle, "w", format=tarfile.PAX_FORMAT) as archive:
        content = {"manifest.json": (json.dumps(manifest, sort_keys=True).encode(), "100644")}
        content.update({"payload/" + name: value for name, value in files.items()})
        for name, (data, mode) in sorted(content.items()):
            info = tarfile.TarInfo(name)
            info.size, info.mode, info.mtime = len(data), int(mode[-3:], 8), 0
            archive.addfile(info, io.BytesIO(data))
    digest = sha256(bundle.read_bytes())
    report = {key: value for key, value in manifest.items() if key != "files"}
    report.update(candidate_sha256=digest, file_count=len(files),
                  qualification="await_completed_main_ci" if manifest["origin_main_push"] else "preview_only",
                  deployment_executed=False)
    (output / "candidate-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (output / "candidate.sha256").write_text(digest + "  candidate.tar\n", encoding="utf-8")
    return report


def verify(bundle: Path, expected_digest: str, source_sha: str) -> tuple[dict, dict[str, bytes]]:
    if not DIGEST.fullmatch(expected_digest) or not SHA.fullmatch(source_sha):
        raise ValueError("Full candidate SHA and SHA-256 are required")
    if bundle.stat().st_size > MAX_BYTES or sha256(bundle.read_bytes()) != expected_digest:
        raise ValueError("Candidate archive digest mismatch")
    content = {}
    with tarfile.open(bundle, "r:") as archive:
        members = archive.getmembers()
        if len(members) > 10000 or sum(member.size for member in members) > MAX_BYTES:
            raise ValueError("Candidate archive exceeds limits")
        for member in members:
            path = PurePosixPath(member.name)
            if (not member.isfile() or path.is_absolute() or ".." in path.parts or "\\" in member.name
                    or str(path) != member.name or member.name in content):
                raise ValueError("Unsafe or duplicate archive member")
            if member.name != "manifest.json" and not member.name.startswith("payload/"):
                raise ValueError("Unexpected candidate member")
            stream = archive.extractfile(member)
            if stream is None:
                raise ValueError("Unreadable candidate member")
            content[member.name] = stream.read()
    manifest = json.loads(content.pop("manifest.json"))
    if manifest["schema_version"] != 1 or manifest["repository"] != REPOSITORY or manifest["source_sha"] != source_sha:
        raise ValueError("Candidate provenance mismatch")
    payload = {name.removeprefix("payload/"): data for name, data in content.items()}
    if not payload or set(payload) != set(manifest["files"]):
        raise ValueError("Candidate inventory mismatch")
    for name, data in payload.items():
        metadata = manifest["files"][name]
        if metadata["mode"] not in ("100644", "100755") or sha256(data) != metadata["sha256"]:
            raise ValueError("Candidate file digest or mode mismatch")
    return manifest, payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(".ci-artifacts/candidate"))
    args = parser.parse_args()
    report = build(ROOT, args.output, dict(os.environ))
    manifest, _ = verify(args.output / "candidate.tar", report["candidate_sha256"], report["source_sha"])
    assert manifest["source_sha"] == report["source_sha"]
    print(json.dumps(report, indent=2))
    summary = os.getenv("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as handle:
            handle.write(f"Candidate `{report['source_sha']}`: `{report['candidate_sha256']}` ({report['qualification']}).\n")


if __name__ == "__main__":
    main()
