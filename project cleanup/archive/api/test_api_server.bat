@echo off
REM Script: test_api_server.bat
REM Purpose: Test REST API server endpoints
REM Part of: Conductor SMS System

echo ========================================
echo   SMSConductor API Server Test
echo ========================================
echo.

cd /d "%~dp0"

echo Testing API server endpoints...
echo Make sure the API server is running first!
echo.

python test_api_server.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Test script failed with error code %ERRORLEVEL%
    pause
    exit /b %ERRORLEVEL%
)

pause
