$ErrorActionPreference = "Stop"

$projectDir = if ($env:FRAUDLENS_DBT_PROJECT_DIR) { $env:FRAUDLENS_DBT_PROJECT_DIR } else { "dbt" }
$profilesDir = if ($env:FRAUDLENS_DBT_PROFILES_DIR) { $env:FRAUDLENS_DBT_PROFILES_DIR } else { "dbt/profiles" }
$profileName = if ($env:FRAUDLENS_DBT_PROFILE_NAME) { $env:FRAUDLENS_DBT_PROFILE_NAME } else { "fraudlens_local_spark" }
$targetName = if ($env:FRAUDLENS_DBT_TARGET_NAME) { $env:FRAUDLENS_DBT_TARGET_NAME } else { "local" }

Write-Host "[dbt] parse ($profileName/$targetName)"
dbt parse `
  --project-dir $projectDir `
  --profiles-dir $profilesDir `
  --profile $profileName `
  --target $targetName

Write-Host "[dbt] ls ($profileName/$targetName)"
dbt ls `
  --project-dir $projectDir `
  --profiles-dir $profilesDir `
  --profile $profileName `
  --target $targetName

Write-Host "[dbt] structure validation succeeded."
