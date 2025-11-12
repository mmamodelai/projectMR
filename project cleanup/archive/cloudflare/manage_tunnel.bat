@echo off
REM Script: manage_tunnel.bat
REM Purpose: Start/stop/status cloudflare tunnel
REM Part of: Conductor SMS System

cd /d "%~dp0"

if not exist "cloudflared.exe" (
    echo ERROR: cloudflared.exe not found!
    pause
    exit /b 1
)

echo Cloudflare Tunnel Manager
echo ========================
echo.
echo 1. Start tunnel
echo 2. Stop tunnel
echo 3. Check tunnel status
echo 4. List tunnels
echo 5. Exit
echo.

set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" (
    echo.
    set /p tunnel_name="Enter tunnel name: "
    echo Starting tunnel: %tunnel_name%
    echo Press Ctrl+C to stop
    cloudflared.exe tunnel run %tunnel_name%
    
) else if "%choice%"=="2" (
    echo.
    echo Stopping Cloudflare service...
    net stop Cloudflared
    echo Service stopped.
    
) else if "%choice%"=="3" (
    echo.
    echo Checking tunnel status...
    sc query Cloudflared
    echo.
    echo Checking active tunnels...
    cloudflared.exe tunnel list
    
) else if "%choice%"=="4" (
    echo.
    echo Listing all tunnels...
    cloudflared.exe tunnel list
    
) else if "%choice%"=="5" (
    echo Goodbye!
    exit /b 0
    
) else (
    echo Invalid choice.
)

pause
