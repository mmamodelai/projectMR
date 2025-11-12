@echo off
REM Script: cloudflare_api_tool.bat
REM Purpose: Execute Cloudflare API tool for token verification
REM Part of: Conductor SMS System

echo Starting Cloudflare API Tool...
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found. Please install Python and try again.
    pause
    exit /b 1
)

REM Check if logs directory exists
if not exist "logs" mkdir logs

REM Run the API tool with default parameters (from your curl command)
echo.
echo Verifying Cloudflare API token...
echo Account ID: ed835396a75f0a35ea698cc764615662
echo Token: 4STsv9xjfAHZK8EmtiRpFdcvAe8UJSSAbZ1zpQpf
echo.

python cloudflare_api_tool.py verify --verbose --account-info

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: API tool failed with code %ERRORLEVEL%
    echo Check logs/cloudflare_api.log for details
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ✅ API tool completed successfully
echo Check logs/cloudflare_api.log for detailed logs
pause
