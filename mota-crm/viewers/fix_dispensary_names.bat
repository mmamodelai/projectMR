@echo off
REM Fix Dispensary Names
REM Part of: Conductor SMS System

echo Fixing dispensary names in budtenders table...
echo.

cd /d "%~dp0"
python fix_dispensary_names.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Script failed with code %ERRORLEVEL%
    pause
    exit /b %ERRORLEVEL%
)

echo.
pause



