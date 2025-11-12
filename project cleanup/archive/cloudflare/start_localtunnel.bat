@echo off
REM Script: start_localtunnel.bat
REM Purpose: Start localtunnel for n8n cloud access
REM Part of: Conductor SMS System

echo ========================================
echo   Starting Localtunnel
echo ========================================
echo Exposing http://localhost:5001 to the internet...
echo.
echo IMPORTANT: Copy the HTTPS URL that appears below
echo It will look like: https://xxxxx.loca.lt
echo.
echo This will run in the background.
echo ========================================

cd /d "%~dp0"

REM Kill any existing localtunnel processes
taskkill /f /im node.exe 2>nul

REM Start localtunnel
start "Localtunnel" /min lt --port 5001

echo Localtunnel started successfully!
echo.
echo The tunnel is now running in the background.
echo Check the Localtunnel window for the public URL.
echo.
echo To stop the tunnel, run: stop_localtunnel.bat
echo.
pause
