$ErrorActionPreference = "Stop"

# Resolve all paths relative to this repository.
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$MainScript = Join-Path $ProjectRoot "main.py"

Set-Location $ProjectRoot

if (-not (Test-Path $VenvPython)) {
    Write-Host "The virtual environment has not been created." -ForegroundColor Yellow
    Write-Host "Running setup.ps1 first..."
    & (Join-Path $ProjectRoot "setup.ps1")
}

if (-not (Test-Path $VenvPython)) {
    throw "Python virtual environment is unavailable."
}

if (-not (Test-Path $MainScript)) {
    throw "main.py was not found at: $MainScript"
}

& $VenvPython $MainScript

exit $LASTEXITCODE
