param(
    [switch]$ForceReinstall
)

$ErrorActionPreference = "Stop"

# Always work from the repository directory,
# regardless of where this script was launched.
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

$VenvPath = Join-Path $ProjectRoot ".venv"
$VenvPython = Join-Path $VenvPath "Scripts\python.exe"
$RequirementsFile = Join-Path $ProjectRoot "requirements.txt"
$RequirementsHashFile = Join-Path $VenvPath ".requirements.sha256"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " RoboMaster Lab Environment Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Project root: $ProjectRoot"

if (-not (Test-Path $RequirementsFile)) {
    throw "requirements.txt was not found at: $RequirementsFile"
}

function Find-Python38 {
    # First try the Windows Python Launcher.
    if (Get-Command py -ErrorAction SilentlyContinue) {
        try {
            $Version = & py -3.8 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))" 2>$null

            if ($Version -eq "3.8") {
                return @{
                    Command = "py"
                    Arguments = @("-3.8")
                }
            }
        }
        catch {
            # Continue to the next detection method.
        }
    }

    # Fall back to a python command available in PATH.
    if (Get-Command python -ErrorAction SilentlyContinue) {
        try {
            $Version = & python -c "import sys; print('.'.join(map(str, sys.version_info[:2])))" 2>$null

            if ($Version -eq "3.8") {
                return @{
                    Command = "python"
                    Arguments = @()
                }
            }
        }
        catch {
            # Python was found but could not be executed.
        }
    }

    return $null
}

if (-not (Test-Path $VenvPython)) {
    Write-Host ""
    Write-Host "No local virtual environment was found." -ForegroundColor Yellow
    Write-Host "Searching for Python 3.8..."

    $Python38 = Find-Python38

    if ($null -eq $Python38) {
        Write-Host ""
        Write-Host "Python 3.8 was not found." -ForegroundColor Red
        Write-Host "Install Python 3.8.x and enable the Python Launcher or add Python to PATH."
        exit 1
    }

    Write-Host "Creating .venv using Python 3.8..." -ForegroundColor Cyan

    if ($Python38.Command -eq "py") {
        & py -3.8 -m venv $VenvPath
    }
    else {
        & python -m venv $VenvPath
    }

    if (-not (Test-Path $VenvPython)) {
        throw "Virtual environment creation failed."
    }
}
else {
    Write-Host ""
    Write-Host "Existing .venv found. Reusing it." -ForegroundColor Green
}

$CurrentPythonVersion = & $VenvPython -c "import sys; print('.'.join(map(str, sys.version_info[:2])))"

if ($CurrentPythonVersion -ne "3.8") {
    throw "The existing .venv uses Python $CurrentPythonVersion instead of Python 3.8. Delete .venv and run setup.ps1 again."
}

$CurrentRequirementsHash = (
    Get-FileHash $RequirementsFile -Algorithm SHA256
).Hash

$SavedRequirementsHash = ""

if (Test-Path $RequirementsHashFile) {
    $SavedRequirementsHash = (
        Get-Content $RequirementsHashFile -Raw
    ).Trim()
}

$NeedsInstallation = (
    $ForceReinstall -or
    -not (Test-Path $RequirementsHashFile) -or
    $CurrentRequirementsHash -ne $SavedRequirementsHash
)

if ($NeedsInstallation) {
    Write-Host ""
    Write-Host "Installing project dependencies..." -ForegroundColor Cyan

    & $VenvPython -m pip install --upgrade "pip==24.3.1"
    & $VenvPython -m pip install "setuptools<70" wheel
    & $VenvPython -m pip install -r $RequirementsFile

    $CurrentRequirementsHash |
        Set-Content $RequirementsHashFile -Encoding ASCII
}
else {
    Write-Host ""
    Write-Host "Dependencies are already up to date." -ForegroundColor Green
}

Write-Host ""
Write-Host "Testing environment..." -ForegroundColor Cyan

& $VenvPython -c "import sys; print('Python:', sys.version); print('Executable:', sys.executable)"
& $VenvPython -c "import robomaster; print('RoboMaster:', robomaster.__file__)"
& $VenvPython -c "from robomaster import robot; print('RoboMaster robot module: OK')"
& $VenvPython -c "import yaml, pandas, matplotlib, cv2, ipykernel; print('Project libraries: OK')"
& $VenvPython -m pip check

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host " Environment is ready" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Run the project with:"
Write-Host ".\run.ps1" -ForegroundColor Yellow
Write-Host ""
Write-Host "Activate manually with:"
Write-Host ".\.venv\Scripts\Activate.ps1" -ForegroundColor Yellow
