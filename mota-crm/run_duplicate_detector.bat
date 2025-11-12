@echo off
REM Script: duplicate_detector.bat
REM Purpose: Run customer duplicate detection
REM Part of: Conductor SMS System

echo Starting Customer Duplicate Detection...
echo.

cd /d "%~dp0"
python duplicate_detector.py

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Duplicate detection failed with code %ERRORLEVEL%
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo Duplicate detection complete!
echo Check the generated CSV and JSON files for results.
pause
