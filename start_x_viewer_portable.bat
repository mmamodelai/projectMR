@echo off
REM Script: start_x_viewer_portable.bat
REM Purpose: Launch X-Viewer Portable (External Budtender Management)
REM Part of: Conductor SMS System

echo Starting X-Viewer Portable...
cd /d "%~dp0x_viewer_portable"
python x_viewer_portable.py
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: X-Viewer Portable failed with code %ERRORLEVEL%
    pause
    exit /b %ERRORLEVEL%
)
pause
