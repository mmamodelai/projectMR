@echo off
REM Script: start_cloudflare_tunnel.bat
REM Purpose: Start Cloudflare Tunnel for SMS Conductor API
REM Part of: Conductor SMS System

echo ========================================
echo   Starting Cloudflare Tunnel
echo ========================================
echo.
echo Exposing http://localhost:5001 to the internet...
echo.
echo IMPORTANT: Copy the HTTPS URL that appears below
echo It will look like: https://xxxxx.trycloudflare.com
echo.
echo ========================================

"%ProgramFiles%\cloudflared\cloudflared.exe" tunnel --url http://localhost:5001

pause

