@echo off
REM Script: start_persistent_tunnel.bat
REM Purpose: Start persistent tunnel with fixed subdomain
REM Part of: Conductor SMS System

echo ========================================
echo   Starting Persistent Tunnel
echo ========================================
echo.

cd /d "%~dp0"

REM Kill any existing localtunnel processes
taskkill /f /im node.exe 2>nul

REM Wait for cleanup
timeout /t 2 /nobreak >nul

REM Start persistent tunnel with fixed subdomain
echo Starting tunnel with subdomain: smsconductor...
echo URL will be: https://smsconductor.loca.lt
echo.
echo Keep this window open!
echo.

npx localtunnel --port 5001 --subdomain smsconductor

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Tunnel failed to start
    echo Try: npm install -g localtunnel
    pause
    exit /b %ERRORLEVEL%
)

pause
