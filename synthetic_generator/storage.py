from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urlparse

from .progress import ProgressReporter


def upload_run_to_minio(run_dir: Path, run_id: str, progress: ProgressReporter | None = None) -> dict:
    endpoint = os.getenv("MINIO_ENDPOINT", "").strip()
    access_key = os.getenv("MINIO_ACCESS_KEY", "").strip()
    secret_key = os.getenv("MINIO_SECRET_KEY", "").strip()
    bucket = os.getenv("MINIO_DEFAULT_BUCKET", "fraudlens-raw").strip() or "fraudlens-raw"
    prefix_root = os.getenv("PHASE2_MINIO_PREFIX", "phase2").strip() or "phase2"

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
            object_name = f"{prefix}/{file_path.relative_to(run_dir).as_posix()}"
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
