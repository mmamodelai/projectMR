@echo off
REM Script: start_SMSconductor_DB.bat
REM Purpose: Launch SMS Conductor Database Viewer
REM Part of: Conductor V4.1 - SMS Message Management

echo Starting SMS Conductor DB Viewer...
cd /d "%~dp0"

REM Try running with pythonw (no console)
pythonw.exe SMSconductor_DB.py

REM If that fails, try with regular python to see errors
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Failed to launch viewer. Trying with console for debugging...
    python.exe SMSconductor_DB.py
    pause
)

