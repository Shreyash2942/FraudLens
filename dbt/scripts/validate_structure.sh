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

MANIFEST_PATH="${PROJECT_DIR}/target/manifest.json"
echo "[dbt] governance/naming/contract checks (${MANIFEST_PATH})"
python "${PROJECT_DIR}/scripts/validate_naming_rules.py" --manifest "${MANIFEST_PATH}"
python "${PROJECT_DIR}/scripts/validate_governance_metadata.py" --manifest "${MANIFEST_PATH}"
python "${PROJECT_DIR}/scripts/validate_contracts.py" --manifest "${MANIFEST_PATH}"
python "${PROJECT_DIR}/scripts/validate_contract_alignment.py" --manifest "${MANIFEST_PATH}"

echo "[dbt] ls (${PROFILE_NAME}/${TARGET_NAME})"
dbt ls \
  --project-dir "${PROJECT_DIR}" \
  --profiles-dir "${PROFILES_DIR}" \
  --profile "${PROFILE_NAME}" \
  --target "${TARGET_NAME}"

echo "[dbt] structure validation succeeded."
