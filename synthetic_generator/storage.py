from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urlparse

from .progress import ProgressReporter


def _first_non_empty_env(*names: str) -> str:
    for name in names:
        value = os.getenv(name, "").strip()
        if value:
            return value
    return ""


def _resolve_minio_config() -> dict[str, str]:
    endpoint = _first_non_empty_env("MINIO_ENDPOINT", "DATALAB_MINIO_ENDPOINT", "DATALAB_MINIO_ENDPOINT_OUTSIDE")
    access_key = _first_non_empty_env("MINIO_ACCESS_KEY", "DATALAB_MINIO_ACCESS_KEY")
    secret_key = _first_non_empty_env("MINIO_SECRET_KEY", "DATALAB_MINIO_SECRET_KEY")
    bucket = _first_non_empty_env("MINIO_DEFAULT_BUCKET", "DATALAB_MINIO_BUCKET") or "fraudlensdata"
    prefix_root = _first_non_empty_env("PHASE2_MINIO_PREFIX") or "fraudlens/synthetic_data/batches"
    return {
        "endpoint": endpoint,
        "access_key": access_key,
        "secret_key": secret_key,
        "bucket": bucket,
        "prefix_root": prefix_root,
    }


def _professional_minio_subpath(path: Path) -> str:
    parts = list(path.parts)
    if len(parts) >= 2 and parts[0] == "landing" and parts[1] == "csv":
        return str(Path("raw_zone") / "csv" / Path(*parts[2:])).replace("\\", "/")
    if parts and parts[0] == "control":
        return str(Path("governance") / "control" / Path(*parts[1:])).replace("\\", "/")
    if parts and parts[0] == "quality":
        return str(Path("governance") / "quality" / Path(*parts[1:])).replace("\\", "/")
    return path.as_posix()


def upload_run_to_minio(run_dir: Path, run_id: str, progress: ProgressReporter | None = None) -> dict:
    config = _resolve_minio_config()
    endpoint = config["endpoint"]
    access_key = config["access_key"]
    secret_key = config["secret_key"]
    bucket = config["bucket"]
    prefix_root = config["prefix_root"]

    if not endpoint or not access_key or not secret_key:
        return {"status": "skipped", "reason": "missing_minio_configuration", "bucket": bucket, "prefix": f"{prefix_root}/{run_id}"}

    try:
        from minio import Minio
    except ImportError:
        return {"status": "skipped", "reason": "minio_package_not_installed", "bucket": bucket, "prefix": f"{prefix_root}/{run_id}"}

    parsed = urlparse(endpoint)
    netloc = parsed.netloc or parsed.path
    secure = parsed.scheme == "https"
    prefix = f"{prefix_root}/{run_id}"

    try:
        client = Minio(netloc, access_key=access_key, secret_key=secret_key, secure=secure)
        if not client.bucket_exists(bucket):
            client.make_bucket(bucket)
        uploaded_files = []
        files = [file_path for file_path in sorted(run_dir.rglob("*")) if file_path.is_file()]
        total = len(files)
        for index, file_path in enumerate(files, start=1):
            if not file_path.is_file():
                continue
            object_subpath = _professional_minio_subpath(file_path.relative_to(run_dir))
            object_name = f"{prefix}/{object_subpath}"
            client.fput_object(bucket, object_name, str(file_path))
            uploaded_files.append(object_name)
            if progress:
                progress.tick(
                    key="minio_upload",
                    current=index,
                    total=total,
                    label="Uploading generated artifacts to MinIO",
                    every=1,
                )
        return {"status": "uploaded", "bucket": bucket, "prefix": prefix, "file_count": len(uploaded_files)}
    except Exception as exc:  # pragma: no cover - runtime/environment-specific
        return {"status": "blocked", "reason": str(exc), "bucket": bucket, "prefix": prefix}
