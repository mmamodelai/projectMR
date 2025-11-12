@echo off
REM Script: setup_cloudflare_tunnel.bat
REM Purpose: Complete Windows cloudflared tunnel setup for n8n
REM Part of: Conductor SMS System

echo ========================================
echo Cloudflare Tunnel Setup for Windows
echo ========================================
echo.
echo This script will set up a persistent tunnel for your n8n instance
echo on your Windows PC with SIM modem.
echo.

cd /d "%~dp0"

REM Check if cloudflared exists
if not exist "cloudflared.exe" (
    echo ERROR: cloudflared.exe not found!
    echo Please run this script from the Olive directory.
    pause
    exit /b 1
)

echo Step 1: Authenticating with Cloudflare...
echo This will open your browser to log in to Cloudflare.
echo.
pause

REM Authenticate with Cloudflare
cloudflared.exe tunnel login

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Authentication failed!
    pause
    exit /b 1
)

echo.
echo Step 2: Creating tunnel...
set /p tunnel_name="Enter tunnel name (e.g., n8n-tunnel): "
if "%tunnel_name%"=="" set tunnel_name=n8n-tunnel

cloudflared.exe tunnel create %tunnel_name%

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Tunnel creation failed!
    pause
    exit /b 1
)

echo.
echo Step 3: Configuring tunnel...
set /p subdomain="Enter subdomain (e.g., n8n): "
if "%subdomain%"=="" set subdomain=n8n

set /p domain="Enter domain (default: marketsuite.co): "
if "%domain%"=="" set domain=marketsuite.co

set /p n8n_port="Enter n8n port (default: 5678): "
if "%n8n_port%"=="" set n8n_port=5678

echo.
echo Creating DNS record: %subdomain%.%domain%
cloudflared.exe tunnel route dns %tunnel_name% %subdomain%.%domain%

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: DNS record creation failed!
    pause
    exit /b 1
)

echo.
echo Step 4: Creating tunnel configuration...
REM Create .cloudflared directory if it doesn't exist
if not exist "%USERPROFILE%\.cloudflared" mkdir "%USERPROFILE%\.cloudflared"

REM Get tunnel ID from the tunnel list
echo Getting tunnel ID...
for /f "tokens=*" %%i in ('cloudflared.exe tunnel list') do (
    echo %%i | findstr /i "%tunnel_name%" >nul
    if !errorlevel! equ 0 (
        for /f "tokens=1" %%j in ("%%i") do set tunnel_id=%%j
    )
)

if "%tunnel_id%"=="" (
    echo ERROR: Could not find tunnel ID!
    echo Please check tunnel list manually.
    cloudflared.exe tunnel list
    pause
    exit /b 1
)

echo Tunnel ID: %tunnel_id%

REM Create config.yml
echo Creating config.yml...
(
echo tunnel: %tunnel_id%
echo credentials-file: %USERPROFILE%\.cloudflared\%tunnel_id%.json
echo ingress:
echo   - hostname: %subdomain%.%domain%
echo     service: http://localhost:%n8n_port%
echo   - service: http_status:404
) > "%USERPROFILE%\.cloudflared\config.yml"

echo.
echo Step 5: Installing as Windows service...
cloudflared.exe service install

if %ERRORLEVEL% NEQ 0 (
    echo WARNING: Service installation failed, but tunnel can still run manually
) else (
    echo Service installed successfully!
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Your n8n tunnel is configured:
echo - Tunnel Name: %tunnel_name%
echo - Tunnel ID: %tunnel_id%
echo - URL: https://%subdomain%.%domain%
echo - Local Service: http://localhost:%n8n_port%
echo.
echo To start the tunnel:
echo 1. Start n8n on port %n8n_port%
echo 2. Run: cloudflared.exe tunnel run %tunnel_name%
echo.
echo Or start the Windows service:
echo net start Cloudflared
echo.
echo Configuration saved to: %USERPROFILE%\.cloudflared\config.yml
echo.

set /p start_now="Start the tunnel now? (y/n): "
if /i "%start_now%"=="y" (
    echo.
    echo Starting tunnel...
    echo Press Ctrl+C to stop
    cloudflared.exe tunnel run %tunnel_name%
) else (
    echo.
    echo To start later, run: cloudflared.exe tunnel run %tunnel_name%
)

pause
