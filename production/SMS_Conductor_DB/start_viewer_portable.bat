@echo off
REM SMS Conductor Database Viewer - Portable Launcher
REM This runs without needing the full Conductor system

echo.
echo ========================================
echo SMS Conductor Database Viewer (Portable)
echo ========================================
echo.

cd /d "%~dp0"

REM Check if .env exists
if not exist ".env" (
    if not exist "config.json" (
        echo [ERROR] No configuration found!
        echo.
        echo Please create EITHER:
        echo   1. .env file with Supabase credentials
        echo   2. config.json with database settings
        echo.
        echo Copy PORTABLE_CONFIG.txt to .env to get started
        echo See PORTABLE_VIEWER_SETUP.md for instructions
        echo.
        pause
        exit /b 1
    )
)

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python not found!
    echo.
    echo Please install Python 3.9+ from python.org
    echo.
    pause
    exit /b 1
)

echo [INFO] Checking dependencies...
python -c "import supabase" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Supabase module not found. Installing...
    pip install supabase python-dateutil python-dotenv
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
)

echo [OK] Starting viewer...
echo.

REM Run with pythonw to hide console (comment out for debugging)
start "SMS Viewer" pythonw SMSconductor_DB.py

REM OR use this line for debugging (shows console)
REM python SMSconductor_DB.py

echo.
echo Viewer launched!
echo If nothing appears, run this with console:
echo    python SMSconductor_DB.py
echo.

timeout /t 3 /nobreak >nul

