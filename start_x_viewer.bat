@echo off
REM Script: start_x_viewer.bat
REM Purpose: Launch X-Viewer (External Budtender Management System)
REM Part of: Conductor SMS System

echo Starting X-Viewer...
cd /d "%~dp0"
python x_viewer.py
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: X-Viewer failed with code %ERRORLEVEL%
    pause
    exit /b %ERRORLEVEL%
)
pause
