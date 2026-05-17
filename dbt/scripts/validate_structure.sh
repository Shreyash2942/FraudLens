#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${FRAUDLENS_DBT_PROJECT_DIR:-dbt}"
PROFILES_DIR="${FRAUDLENS_DBT_PROFILES_DIR:-dbt/profiles}"
PROFILE_NAME="${FRAUDLENS_DBT_PROFILE_NAME:-fraudlens_local_spark}"
TARGET_NAME="${FRAUDLENS_DBT_TARGET_NAME:-local}"

echo "[dbt] parse (${PROFILE_NAME}/${TARGET_NAME})"
dbt parse \
  --project-dir "${PROJECT_DIR}" \
  --profiles-dir "${PROFILES_DIR}" \
  --profile "${PROFILE_NAME}" \
  --target "${TARGET_NAME}"

echo "[dbt] ls (${PROFILE_NAME}/${TARGET_NAME})"
dbt ls \
  --project-dir "${PROJECT_DIR}" \
  --profiles-dir "${PROFILES_DIR}" \
  --profile "${PROFILE_NAME}" \
  --target "${TARGET_NAME}"

echo "[dbt] structure validation succeeded."
