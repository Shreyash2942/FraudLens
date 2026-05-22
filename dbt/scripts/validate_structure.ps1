$ErrorActionPreference = "Stop"

$projectDir = if ($env:FRAUDLENS_DBT_PROJECT_DIR) { $env:FRAUDLENS_DBT_PROJECT_DIR } else { "dbt" }
$profilesDir = if ($env:FRAUDLENS_DBT_PROFILES_DIR) { $env:FRAUDLENS_DBT_PROFILES_DIR } else { "dbt/profiles" }
$profileName = if ($env:FRAUDLENS_DBT_PROFILE_NAME) { $env:FRAUDLENS_DBT_PROFILE_NAME } else { "fraudlens_local_spark" }
$targetName = if ($env:FRAUDLENS_DBT_TARGET_NAME) { $env:FRAUDLENS_DBT_TARGET_NAME } else { "local" }
$validationMode = if ($env:FRAUDLENS_VALIDATION_MODE) { $env:FRAUDLENS_VALIDATION_MODE } else { "strict" }

Write-Host "[dbt] parse ($profileName/$targetName)"
dbt parse `
  --project-dir $projectDir `
  --profiles-dir $profilesDir `
  --profile $profileName `
  --target $targetName

$manifestPath = Join-Path $projectDir "target/manifest.json"
Write-Host "[dbt] validation mode ($validationMode)"
Write-Host "[dbt] gate coverage checks ($profileName/$targetName)"
$criticalGateCount = dbt ls `
  --resource-type test `
  --selector failure_blocking_gate `
  --project-dir $projectDir `
  --profiles-dir $profilesDir `
  --profile $profileName `
  --target $targetName | Measure-Object -Line | Select-Object -ExpandProperty Lines

if ($criticalGateCount -eq 0) {
  throw "[dbt] ERROR: failure_blocking_gate resolved to zero tests"
}

if ($validationMode -eq "diagnostic") {
  $diagnosticGateCount = dbt ls `
    --resource-type test `
    --selector failure_diagnostic_gate `
    --project-dir $projectDir `
    --profiles-dir $profilesDir `
    --profile $profileName `
    --target $targetName | Measure-Object -Line | Select-Object -ExpandProperty Lines

  if ($diagnosticGateCount -eq 0) {
    throw "[dbt] ERROR: failure_diagnostic_gate resolved to zero tests"
  }
}

Write-Host "[dbt] governance/naming/contract checks ($manifestPath)"
python (Join-Path $projectDir "scripts/validate_naming_rules.py") --manifest $manifestPath
python (Join-Path $projectDir "scripts/validate_governance_metadata.py") --manifest $manifestPath
python (Join-Path $projectDir "scripts/validate_contracts.py") --manifest $manifestPath
python (Join-Path $projectDir "scripts/validate_contract_alignment.py") --manifest $manifestPath
python (Join-Path $projectDir "scripts/validate_failure_policy.py") --manifest $manifestPath --selectors (Join-Path $projectDir "selectors.yml") --policy (Join-Path $projectDir "tests/validation/failure_policy_matrix.json")

Write-Host "[dbt] ls ($profileName/$targetName)"
dbt ls `
  --project-dir $projectDir `
  --profiles-dir $profilesDir `
  --profile $profileName `
  --target $targetName

Write-Host "[dbt] structure validation succeeded."
