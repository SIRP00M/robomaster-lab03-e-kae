@echo off
setlocal EnableExtensions

title RoboMaster Lab Runner

REM Always run from the directory containing this script.
cd /d "%~dp0"

set "PROJECT_ROOT=%CD%"
set "VENV_PYTHON=%PROJECT_ROOT%\.venv\Scripts\python.exe"
set "MAIN_SCRIPT=%PROJECT_ROOT%\main.py"
set "SETUP_SCRIPT=%PROJECT_ROOT%\setup.bat"

if not exist "%VENV_PYTHON%" (
    echo [INFO] Local environment was not found.
    echo [INFO] Running setup.bat...
    echo.

    call "%SETUP_SCRIPT%"

    if errorlevel 1 (
        echo.
        echo [ERROR] Environment setup failed.
        pause
        exit /b 1
    )
)

if not exist "%MAIN_SCRIPT%" (
    echo [ERROR] main.py was not found.
    echo Expected path:
    echo %MAIN_SCRIPT%
    pause
    exit /b 1
)

echo ========================================
echo  Starting RoboMaster Lab
echo ========================================
echo Python:
"%VENV_PYTHON%" -c "import sys; print(sys.executable)"
echo.

"%VENV_PYTHON%" "%MAIN_SCRIPT%"

set "EXIT_CODE=%ERRORLEVEL%"

echo.
if "%EXIT_CODE%"=="0" (
    echo [INFO] Program finished successfully.
) else (
    echo [ERROR] Program exited with code %EXIT_CODE%.
)

pause
exit /b %EXIT_CODE%