@echo off
REM Script: start_dispensary_viewer.bat
REM Purpose: Launch the Dispensary & Budtender Viewer
REM Part of: Conductor SMS System

echo Starting Dispensary & Budtender Viewer...
echo.

REM Check if Python is available
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found. Please install Python.
    pause
    exit /b 1
)

echo Launching Supabase-powered viewer...
python dispensary_viewer.py

pause
