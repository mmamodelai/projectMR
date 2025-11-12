@echo off
REM Script: cloudflare_tunnel_manager.bat
REM Purpose: Manage Cloudflare tunnels for n8n integration
REM Part of: Conductor SMS System

echo Starting Cloudflare Tunnel Manager...
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

echo.
echo Cloudflare Tunnel Manager
echo ========================
echo.
echo Available commands:
echo 1. List existing tunnels
echo 2. Create new tunnel for n8n
echo 3. Delete tunnel
echo 4. Exit
echo.

set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    echo.
    echo Listing existing tunnels...
    python cloudflare_tunnel_manager.py list --verbose
) else if "%choice%"=="2" (
    echo.
    echo Creating new tunnel for n8n...
    echo.
    set /p tunnel_name="Enter tunnel name (e.g., n8n-tunnel): "
    set /p subdomain="Enter subdomain (e.g., n8n): "
    set /p zone_id="Enter your Cloudflare Zone ID: "
    set /p domain="Enter domain (default: marketsuite.co): "
    
    if "%domain%"=="" set domain=marketsuite.co
    
    echo.
    echo Creating tunnel: %tunnel_name%
    echo Subdomain: %subdomain%.%domain%
    echo Zone ID: %zone_id%
    echo.
    
    python cloudflare_tunnel_manager.py create --name "%tunnel_name%" --subdomain "%subdomain%" --zone-id "%zone_id%" --domain "%domain%" --verbose
    
) else if "%choice%"=="3" (
    echo.
    set /p tunnel_id="Enter tunnel ID to delete: "
    echo.
    echo Deleting tunnel: %tunnel_id%
    python cloudflare_tunnel_manager.py delete --tunnel-id "%tunnel_id%" --verbose
    
) else if "%choice%"=="4" (
    echo Goodbye!
    exit /b 0
) else (
    echo Invalid choice. Please run the script again.
)

echo.
echo Check logs/cloudflare_tunnels.log for detailed logs
pause
