@echo off
REM Script: start_conductor.bat
REM Purpose: Start Conductor SMS System v2.0
REM Part of: Conductor SMS System

echo ========================================
echo   CONDUCTOR SMS SYSTEM v2.0
echo ========================================
echo.
echo Starting conductor system...
echo.

cd /d "%~dp0"

REM Prevent multiple instances (single-instance guard)
set "RUNNING="
for /f "tokens=*" %%A in ('tasklist /FI "IMAGENAME eq python.exe" /V ^| findstr /I "conductor_system.py"') do set RUNNING=1
for /f "tokens=*" %%A in ('tasklist /FI "IMAGENAME eq pythonw.exe" /V ^| findstr /I "conductor_system.py"') do set RUNNING=1
if defined RUNNING (
    echo [INFO] Conductor already running. Aborting start to avoid COM port contention.
    echo Tip: Run "is_conductor_running.bat" or "STOP_CONDUCTOR.bat" first.
    pause
    exit /b 0
)

REM Check if Python is available
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found in PATH
    echo Please install Python 3.8+ and add to PATH
    pause
    exit /b 1
)

REM Check if config file exists
if not exist "config.json" (
    echo ERROR: config.json not found
    echo Please create configuration file first
    pause
    exit /b 1
)

REM Start conductor
python conductor_system.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Conductor system exited with error code %ERRORLEVEL%
    pause
    exit /b %ERRORLEVEL%
)

pause

