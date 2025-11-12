@echo off
REM Script: start_n8n_with_tunnel.bat
REM Purpose: Start n8n and cloudflare tunnel together
REM Part of: Conductor SMS System

echo ========================================
echo Starting n8n with Cloudflare Tunnel
echo ========================================
echo.

cd /d "%~dp0"

REM Check if cloudflared exists
if not exist "cloudflared.exe" (
    echo ERROR: cloudflared.exe not found!
    echo Please run setup_cloudflare_tunnel.bat first.
    pause
    exit /b 1
)

REM Check if n8n is installed
where n8n >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: n8n not found in PATH!
    echo Please install n8n first: npm install -g n8n
    pause
    exit /b 1
)

echo Starting n8n on port 5678...
echo Starting Cloudflare tunnel...
echo.
echo Your n8n will be accessible at: https://n8n.marketsuite.co
echo (or whatever subdomain you configured)
echo.
echo Press Ctrl+C to stop both services
echo.

REM Start n8n in background
start /b n8n start

REM Wait a moment for n8n to start
timeout /t 5 /nobreak >nul

REM Start the tunnel (this will run in foreground)
cloudflared.exe tunnel run n8n-tunnel

REM If we get here, the tunnel stopped
echo.
echo Tunnel stopped. Stopping n8n...
taskkill /f /im node.exe >nul 2>&1
echo Both services stopped.
pause
