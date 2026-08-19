param(
    [switch]$WithTools,
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$requirements = if ($WithTools) { "requirements-tools.txt" } else { "requirements.txt" }

Push-Location $projectRoot
try {
    & $Python -m pip install --disable-pip-version-check -r $requirements
    if ($LASTEXITCODE -ne 0) { throw "Dependency installation failed." }

    $checkArgs = @("scripts/check_environment.py")
    if ($WithTools) { $checkArgs += "--tools" }
    & $Python @checkArgs
    if ($LASTEXITCODE -ne 0) { throw "Environment validation failed." }

    Write-Host "Environment is ready."
}
finally {
    Pop-Location
}
