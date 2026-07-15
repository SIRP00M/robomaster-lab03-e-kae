@echo off
setlocal EnableExtensions EnableDelayedExpansion

title RoboMaster Lab Environment Setup

REM Always run from the directory containing this script.
cd /d "%~dp0"

set "PROJECT_ROOT=%CD%"
set "VENV_DIR=%PROJECT_ROOT%\.venv"
set "VENV_PYTHON=%VENV_DIR%\Scripts\python.exe"
set "REQUIREMENTS=%PROJECT_ROOT%\requirements.txt"

echo ========================================
echo  RoboMaster Lab Environment Setup
echo ========================================
echo Project root: %PROJECT_ROOT%
echo.

if not exist "%REQUIREMENTS%" (
    echo [ERROR] requirements.txt was not found.
    echo Expected path:
    echo %REQUIREMENTS%
    pause
    exit /b 1
)

REM Reuse an existing virtual environment.
if exist "%VENV_PYTHON%" (
    echo [INFO] Existing .venv found.
    goto CHECK_ENVIRONMENT
)

echo [INFO] Local .venv was not found.
echo [INFO] Searching for Python 3.8...
echo.

REM Try the Windows Python Launcher first.
where py >nul 2>&1
if not errorlevel 1 (
    py -3.8 -c "import sys; exit(0 if sys.version_info[:2] == (3, 8) else 1)" >nul 2>&1
    if not errorlevel 1 (
        echo [INFO] Python 3.8 found through py launcher.
        py -3.8 -m venv "%VENV_DIR%"
        goto VERIFY_VENV
    )
)

REM Fall back to python on PATH.
where python >nul 2>&1
if not errorlevel 1 (
    python -c "import sys; exit(0 if sys.version_info[:2] == (3, 8) else 1)" >nul 2>&1
    if not errorlevel 1 (
        echo [INFO] Python 3.8 found through PATH.
        python -m venv "%VENV_DIR%"
        goto VERIFY_VENV
    )
)

echo [ERROR] Python 3.8 was not found.
echo.
echo Install Python 3.8.x and make sure one of these works:
echo   py -3.8 --version
echo   python --version
echo.
pause
exit /b 1

:VERIFY_VENV
if not exist "%VENV_PYTHON%" (
    echo [ERROR] Failed to create the virtual environment.
    pause
    exit /b 1
)

:CHECK_ENVIRONMENT
echo.
echo [INFO] Checking Python version...

"%VENV_PYTHON%" -c "import sys; print('.'.join(map(str, sys.version_info[:2])))" > "%TEMP%\robomaster_python_version.txt"

set /p PYTHON_VERSION=<"%TEMP%\robomaster_python_version.txt"
del "%TEMP%\robomaster_python_version.txt" >nul 2>&1

if not "%PYTHON_VERSION%"=="3.8" (
    echo [ERROR] The existing .venv uses Python %PYTHON_VERSION%.
    echo Delete the .venv folder and run setup.bat again.
    pause
    exit /b 1
)

echo [INFO] Using Python %PYTHON_VERSION%
echo [INFO] Python executable:
"%VENV_PYTHON%" -c "import sys; print(sys.executable)"
echo.

echo [INFO] Installing packaging tools...
"%VENV_PYTHON%" -m pip install --upgrade "pip==24.3.1"
if errorlevel 1 goto INSTALL_ERROR

"%VENV_PYTHON%" -m pip install "setuptools<70" wheel
if errorlevel 1 goto INSTALL_ERROR

echo.
echo [INFO] Installing Python 3.8 compatible pywinpty...
"%VENV_PYTHON%" -m pip install --only-binary=:all: "pywinpty==2.0.12"
if errorlevel 1 goto INSTALL_ERROR

echo.
echo [INFO] Installing project dependencies...
"%VENV_PYTHON%" -m pip install -r "%REQUIREMENTS%"
if errorlevel 1 goto INSTALL_ERROR

echo.
echo [INFO] Testing environment...

"%VENV_PYTHON%" -c "from robomaster import robot; print('RoboMaster: OK')"
if errorlevel 1 goto TEST_ERROR

"%VENV_PYTHON%" -c "import yaml, pandas, matplotlib, cv2, ipykernel; print('Project libraries: OK')"
if errorlevel 1 goto TEST_ERROR

"%VENV_PYTHON%" -m pip check
if errorlevel 1 goto TEST_ERROR

echo.
echo ========================================
echo  Environment is ready
echo ========================================
echo.
echo Run the project with:
echo   run.bat
echo.
pause
exit /b 0

:INSTALL_ERROR
echo.
echo [ERROR] Dependency installation failed.
echo Check the messages above for details.
pause
exit /b 1

:TEST_ERROR
echo.
echo [ERROR] Environment validation failed.
echo Check the messages above for details.
pause
exit /b 1