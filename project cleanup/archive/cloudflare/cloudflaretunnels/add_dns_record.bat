@echo off
REM Script: add_dns_record.bat
REM Purpose: Add DNS CNAME record for Cloudflare Tunnel subdomain
REM Part of: Conductor SMS System

echo ========================================
echo   Cloudflare DNS Record Manager
echo ========================================
echo.

REM Configuration
set DNS_TOKEN=4STsv9xjfAHZK8EmtiRpFdcvAe8UJSSAbZ1zpQpf
set ZONE_NAME=marketsuite.co
set SUBDOMAIN=%1
set TUNNEL_ID=%2

if "%SUBDOMAIN%"=="" (
    echo Usage: add_dns_record.bat ^<subdomain^> ^<tunnel-id^>
    echo Example: add_dns_record.bat smsn8n 2fbac668-5ee0-4ad7-aee6-208dd57d4d86
    pause
    exit /b 1
)

if "%TUNNEL_ID%"=="" (
    echo Usage: add_dns_record.bat ^<subdomain^> ^<tunnel-id^>
    echo Example: add_dns_record.bat smsn8n 2fbac668-5ee0-4ad7-aee6-208dd57d4d86
    pause
    exit /b 1
)

echo Adding DNS record: %SUBDOMAIN%.%ZONE_NAME% -> %TUNNEL_ID%.cfargotunnel.com
echo.

REM Get zone ID
echo Getting zone ID for %ZONE_NAME%...
for /f "tokens=2 delims=:" %%a in ('curl -s -X GET "https://api.cloudflare.com/client/v4/zones?name=%ZONE_NAME%" -H "Authorization: Bearer %DNS_TOKEN%" -H "Content-Type: application/json" ^| findstr "id"') do (
    set ZONE_ID=%%a
    set ZONE_ID=!ZONE_ID:"=!
    set ZONE_ID=!ZONE_ID:,=!
    set ZONE_ID=!ZONE_ID: =!
)

if "%ZONE_ID%"=="" (
    echo ERROR: Could not get zone ID for %ZONE_NAME%
    pause
    exit /b 1
)

echo Zone ID: %ZONE_ID%
echo.

REM Create DNS record
echo Creating CNAME record...
curl -X POST "https://api.cloudflare.com/client/v4/zones/%ZONE_ID%/dns_records" ^
  -H "Authorization: Bearer %DNS_TOKEN%" ^
  -H "Content-Type: application/json" ^
  --data "{\"type\":\"CNAME\",\"name\":\"%SUBDOMAIN%\",\"content\":\"%TUNNEL_ID%.cfargotunnel.com\",\"proxied\":true}"

echo.
echo ========================================
echo   DNS Record Added Successfully!
echo ========================================
echo.
echo Your tunnel is now available at:
echo   https://%SUBDOMAIN%.%ZONE_NAME%
echo.
echo Test it with:
echo   curl https://%SUBDOMAIN%.%ZONE_NAME%/api/health
echo.
pause
