@echo off
REM Script: setup_complete_tunnel.bat
REM Purpose: Complete tunnel setup - create tunnel, add DNS, and start
REM Part of: Conductor SMS System

echo ========================================
echo   Complete Cloudflare Tunnel Setup
echo ========================================
echo.

REM Configuration
set TUNNEL_NAME=%1
set SUBDOMAIN=%2

if "%TUNNEL_NAME%"=="" (
    echo Usage: setup_complete_tunnel.bat ^<tunnel-name^> ^<subdomain^>
    echo Example: setup_complete_tunnel.bat smsn8n smsn8n
    pause
    exit /b 1
)

if "%SUBDOMAIN%"=="" (
    echo Usage: setup_complete_tunnel.bat ^<tunnel-name^> ^<subdomain^>
    echo Example: setup_complete_tunnel.bat smsn8n smsn8n
    pause
    exit /b 1
)

echo Setting up tunnel: %TUNNEL_NAME%
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
echo Step 2: Creating configuration...
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

REM Step 3: Get tunnel ID from credentials file
echo Step 3: Getting tunnel ID...
for /f "tokens=2 delims=:" %%a in ('type "C:\Users\%USERNAME%\.cloudflared\%TUNNEL_NAME%.json" ^| findstr "TunnelID"') do (
    set TUNNEL_ID=%%a
    set TUNNEL_ID=!TUNNEL_ID:"=!
    set TUNNEL_ID=!TUNNEL_ID:,=!
    set TUNNEL_ID=!TUNNEL_ID: =!
)

if "%TUNNEL_ID%"=="" (
    echo ERROR: Could not get tunnel ID
    pause
    exit /b 1
)

echo Tunnel ID: %TUNNEL_ID%
echo.

REM Step 4: Add DNS record
echo Step 4: Adding DNS record...
python add_dns_record.py --subdomain %SUBDOMAIN% --tunnel-id %TUNNEL_ID%

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to add DNS record
    pause
    exit /b 1
)

echo.
echo Step 5: Starting tunnel...
echo.
echo ========================================
echo   Tunnel Setup Complete!
echo ========================================
echo.
echo Your tunnel is now available at:
echo   https://%SUBDOMAIN%.marketsuite.co
echo.
echo Test it with:
echo   curl https://%SUBDOMAIN%.marketsuite.co/api/health
echo.
echo Starting tunnel (press Ctrl+C to stop)...
echo.

cloudflared.exe tunnel --config tunnel-config.yml run %TUNNEL_NAME%

pause
