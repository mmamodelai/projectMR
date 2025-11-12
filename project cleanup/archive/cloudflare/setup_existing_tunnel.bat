@echo off
REM Script: setup_existing_tunnel.bat
REM Purpose: Configure existing smsn8n tunnel for n8n
REM Part of: Conductor SMS System

echo ========================================
echo Configuring Existing Tunnel for n8n
echo ========================================
echo.

cd /d "%~dp0"

REM Check if cloudflared exists
if not exist "cloudflared.exe" (
    echo ERROR: cloudflared.exe not found!
    pause
    exit /b 1
)

echo Found existing tunnel: smsn8n
echo Tunnel ID: 2fbac668-5ee0-4ad7-aee6-208dd57d4d86
echo.

set /p subdomain="Enter subdomain for n8n (e.g., n8n): "
if "%subdomain%"=="" set subdomain=n8n

set /p domain="Enter domain (default: marketsuite.co): "
if "%subdomain%"=="" set domain=marketsuite.co

set /p n8n_port="Enter n8n port (default: 5678): "
if "%n8n_port%"=="" set n8n_port=5678

echo.
echo Setting up DNS route: %subdomain%.%domain%
cloudflared.exe tunnel route dns smsn8n %subdomain%.%domain%

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: DNS route setup failed!
    pause
    exit /b 1
)

echo.
echo Creating tunnel configuration...
REM Create .cloudflared directory if it doesn't exist
if not exist "%USERPROFILE%\.cloudflared" mkdir "%USERPROFILE%\.cloudflared"

REM Create config.yml
echo Creating config.yml...
(
echo tunnel: 2fbac668-5ee0-4ad7-aee6-208dd57d4d86
echo credentials-file: %USERPROFILE%\.cloudflared\2fbac668-5ee0-4ad7-aee6-208dd57d4d86.json
echo ingress:
echo   - hostname: %subdomain%.%domain%
echo     service: http://localhost:%n8n_port%
echo   - service: http_status:404
) > "%USERPROFILE%\.cloudflared\config.yml"

echo.
echo Installing as Windows service...
cloudflared.exe service install

if %ERRORLEVEL% NEQ 0 (
    echo WARNING: Service installation failed, but tunnel can still run manually
) else (
    echo Service installed successfully!
)

echo.
echo ========================================
echo Configuration Complete!
echo ========================================
echo.
echo Your n8n tunnel is configured:
echo - Tunnel Name: smsn8n
echo - Tunnel ID: 2fbac668-5ee0-4ad7-aee6-208dd57d4d86
echo - URL: https://%subdomain%.%domain%
echo - Local Service: http://localhost:%n8n_port%
echo.
echo Configuration saved to: %USERPROFILE%\.cloudflared\config.yml
echo.

set /p start_now="Start the tunnel now? (y/n): "
if /i "%start_now%"=="y" (
    echo.
    echo Starting tunnel...
    echo Press Ctrl+C to stop
    cloudflared.exe tunnel run smsn8n
) else (
    echo.
    echo To start later, run: cloudflared.exe tunnel run smsn8n
    echo Or start the Windows service: net start Cloudflared
)

pause
