@echo off
REM Script: modem_health.bat
REM Purpose: Check modem health
REM Part of: Conductor SMS System

echo ========================================
echo   CONDUCTOR SMS SYSTEM v2.0
echo   Modem Health Check
echo ========================================
echo.

cd /d "%~dp0"

python conductor_system.py health

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Health check failed
    pause
    exit /b %ERRORLEVEL%
)

pause

