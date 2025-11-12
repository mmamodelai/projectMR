@echo off
REM Script: start_tunnel.bat
REM Purpose: Start localtunnel and keep it running
REM Part of: Conductor SMS System

echo ========================================
echo   Starting Localtunnel
echo ========================================
echo Exposing http://localhost:5001 to the internet...
echo.
echo IMPORTANT: Copy the HTTPS URL that appears below
echo It will look like: https://xxxxx.loca.lt
echo.
echo This will stay open and keep the tunnel active.
echo Close this window to stop the tunnel.
echo ========================================

cd /d "%~dp0"

REM Kill any existing localtunnel processes
taskkill /f /im node.exe 2>nul

REM Start localtunnel and keep it running
lt --port 5001

pause
