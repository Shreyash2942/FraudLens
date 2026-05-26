#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${FRAUDLENS_DBT_PROJECT_DIR:-dbt}"
PROFILES_DIR="${FRAUDLENS_DBT_PROFILES_DIR:-dbt/profiles}"
PROFILE_NAME="${FRAUDLENS_DBT_PROFILE_NAME:-fraudlens_local_spark}"
TARGET_NAME="${FRAUDLENS_DBT_TARGET_NAME:-local}"
VALIDATION_MODE="${FRAUDLENS_VALIDATION_MODE:-strict}"

echo "[dbt] parse (${PROFILE_NAME}/${TARGET_NAME})"
dbt parse \
  --project-dir "${PROJECT_DIR}" \
  --profiles-dir "${PROFILES_DIR}" \
  --profile "${PROFILE_NAME}" \
  --target "${TARGET_NAME}"

MANIFEST_PATH="${PROJECT_DIR}/target/manifest.json"
echo "[dbt] validation mode (${VALIDATION_MODE})"
echo "[dbt] gate coverage checks (${PROFILE_NAME}/${TARGET_NAME})"
CRITICAL_GATE_COUNT="$(
  dbt ls \
    --resource-type test \
    --selector failure_blocking_gate \
    --project-dir "${PROJECT_DIR}" \
    --profiles-dir "${PROFILES_DIR}" \
    --profile "${PROFILE_NAME}" \
    --target "${TARGET_NAME}" | wc -l | tr -d ' '
)"

if [ "${CRITICAL_GATE_COUNT}" -eq 0 ]; then
  echo "[dbt] ERROR: failure_blocking_gate resolved to zero tests"
  exit 1
fi

if [ "${VALIDATION_MODE}" = "diagnostic" ]; then
  DIAGNOSTIC_GATE_COUNT="$(
    dbt ls \
      --resource-type test \
      --selector failure_diagnostic_gate \
      --project-dir "${PROJECT_DIR}" \
      --profiles-dir "${PROFILES_DIR}" \
      --profile "${PROFILE_NAME}" \
      --target "${TARGET_NAME}" | wc -l | tr -d ' '
  )"

  if [ "${DIAGNOSTIC_GATE_COUNT}" -eq 0 ]; then
    echo "[dbt] ERROR: failure_diagnostic_gate resolved to zero tests"
    exit 1
  fi
fi

echo "[dbt] governance/naming/contract checks (${MANIFEST_PATH})"
python "${PROJECT_DIR}/scripts/validate_naming_rules.py" --manifest "${MANIFEST_PATH}"
python "${PROJECT_DIR}/scripts/validate_governance_metadata.py" --manifest "${MANIFEST_PATH}"
python "${PROJECT_DIR}/scripts/validate_contracts.py" --manifest "${MANIFEST_PATH}"
python "${PROJECT_DIR}/scripts/validate_contract_alignment.py" --manifest "${MANIFEST_PATH}"
python "${PROJECT_DIR}/scripts/validate_failure_policy.py" --manifest "${MANIFEST_PATH}" --selectors "${PROJECT_DIR}/selectors.yml" --policy "${PROJECT_DIR}/tests/validation/failure_policy_matrix.json"

echo "[dbt] ls (${PROFILE_NAME}/${TARGET_NAME})"
dbt ls \
  --project-dir "${PROJECT_DIR}" \
  --profiles-dir "${PROFILES_DIR}" \
  --profile "${PROFILE_NAME}" \
  --target "${TARGET_NAME}"

echo "[dbt] structure validation succeeded."
