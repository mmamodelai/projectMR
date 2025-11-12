@echo off
REM Script: create_n8n_tunnel.bat
REM Purpose: Create persistent tunnel for n8n integration
REM Part of: Conductor SMS System

echo Creating n8n Tunnel...
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
echo ========================================
echo Cloudflare Tunnel Setup for n8n
echo ========================================
echo.
echo This will create a persistent tunnel for your n8n instance.
echo You'll need:
echo 1. Cloudflare Zone ID (for marketsuite.co)
echo 2. API token with Tunnel:Edit and DNS:Edit permissions
echo.

set /p zone_id="Enter your Cloudflare Zone ID: "
set /p subdomain="Enter subdomain (default: n8n): "

if "%subdomain%"=="" set subdomain=n8n

echo.
echo Creating tunnel with these settings:
echo - Tunnel name: n8n-tunnel
echo - Subdomain: %subdomain%.marketsuite.co
echo - Zone ID: %zone_id%
echo - Domain: marketsuite.co
echo.

set /p confirm="Continue? (y/n): "
if /i not "%confirm%"=="y" (
    echo Cancelled.
    pause
    exit /b 0
)

echo.
echo Creating tunnel...
python cloudflare_tunnel_manager.py create --name "n8n-tunnel" --subdomain "%subdomain%" --zone-id "%zone_id%" --domain "marketsuite.co" --verbose

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Tunnel creation failed
    echo Check logs/cloudflare_tunnels.log for details
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ========================================
echo Tunnel Created Successfully!
echo ========================================
echo.
echo Your n8n instance will be accessible at:
echo https://%subdomain%.marketsuite.co
echo.
echo Next steps:
echo 1. Install cloudflared on your server
echo 2. Get the tunnel token (run: python cloudflare_tunnel_manager.py get-token --tunnel-id <TUNNEL_ID>)
echo 3. Run: cloudflared tunnel --no-autoupdate run --token <TUNNEL_TOKEN>
echo 4. Configure n8n to listen on localhost:5678
echo.
echo Check logs/cloudflare_tunnels.log for detailed information
pause
