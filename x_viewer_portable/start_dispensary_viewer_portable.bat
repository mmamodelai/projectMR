@echo off
REM Script: start_dispensary_viewer_portable.bat
REM Purpose: Launch the Portable Dispensary & Budtender Viewer
REM Part of: Conductor SMS System

echo Starting Portable Dispensary & Budtender Viewer...
echo.

REM Check if Python is available
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found. Please install Python from python.org
    echo.
    echo This viewer requires Python 3.7 or higher.
    pause
    exit /b 1
)

echo Checking for required packages...
python -c "import supabase" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Installing required package: supabase
    pip install supabase
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to install supabase package.
        echo Please run: pip install supabase
        pause
        exit /b 1
    )
)

echo Launching viewer...
python dispensary_viewer_portable.py

pause
