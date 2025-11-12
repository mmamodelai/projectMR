@echo off
REM Script: create_tunnel.bat
REM Purpose: Create and configure Cloudflare Tunnel for SMS Conductor
REM Part of: Conductor SMS System

echo ========================================
echo   Cloudflare Tunnel Setup
echo ========================================
echo.

REM Configuration
set TUNNEL_NAME=%1
set SUBDOMAIN=%2

if "%TUNNEL_NAME%"=="" (
    echo Usage: create_tunnel.bat ^<tunnel-name^> ^<subdomain^>
    echo Example: create_tunnel.bat smsn8n smsn8n
    pause
    exit /b 1
)

if "%SUBDOMAIN%"=="" (
    echo Usage: create_tunnel.bat ^<tunnel-name^> ^<subdomain^>
    echo Example: create_tunnel.bat smsn8n smsn8n
    pause
    exit /b 1
)

echo Creating tunnel: %TUNNEL_NAME%
echo Subdomain: %SUBDOMAIN%.marketsuite.co
echo.

REM Step 1: Create tunnel
echo Step 1: Creating tunnel...
cloudflared.exe tunnel create %TUNNEL_NAME%

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to create tunnel
    pause
    exit /b 1
)

echo.
echo Step 2: Creating tunnel configuration...
echo.

REM Step 2: Create config file
echo tunnel: %TUNNEL_NAME% > tunnel-config.yml
echo credentials-file: C:\Users\%USERNAME%\.cloudflared\%TUNNEL_NAME%.json >> tunnel-config.yml
echo. >> tunnel-config.yml
echo ingress: >> tunnel-config.yml
echo   - hostname: %SUBDOMAIN%.marketsuite.co >> tunnel-config.yml
echo     service: http://localhost:5001 >> tunnel-config.yml
echo   - service: http_status:404 >> tunnel-config.yml

echo Configuration file created: tunnel-config.yml
echo.

REM Step 3: Run tunnel
echo Step 3: Starting tunnel...
echo.
echo Tunnel will run in background. Press Ctrl+C to stop.
echo.
echo Your tunnel will be available at:
echo   https://%SUBDOMAIN%.marketsuite.co
echo.
echo NOTE: You still need to add the DNS record!
echo Run: add_dns_record.bat %SUBDOMAIN% ^<tunnel-id^>
echo.

cloudflared.exe tunnel --config tunnel-config.yml run %TUNNEL_NAME%

pause
