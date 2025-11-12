@echo off
REM Script: test_tunnel.bat
REM Purpose: Test cloudflare tunnel connection
REM Part of: Conductor SMS System

cd /d "%~dp0"

echo Testing Cloudflare Tunnel Setup
echo ================================
echo.

REM Check if cloudflared exists
if not exist "cloudflared.exe" (
    echo [FAIL] cloudflared.exe not found
    echo Please run setup_cloudflare_tunnel.bat first
    goto :end
) else (
    echo [PASS] cloudflared.exe found
)

REM Check cloudflared version
echo.
echo Cloudflared version:
cloudflared.exe --version

REM Check if authenticated
echo.
echo Checking authentication...
if exist "%USERPROFILE%\.cloudflared\cert.pem" (
    echo [PASS] Cloudflare authentication found
) else (
    echo [FAIL] Not authenticated with Cloudflare
    echo Run: cloudflared.exe tunnel login
)

REM Check tunnel configuration
echo.
echo Checking tunnel configuration...
if exist "%USERPROFILE%\.cloudflared\config.yml" (
    echo [PASS] Tunnel configuration found
    echo.
    echo Configuration:
    type "%USERPROFILE%\.cloudflared\config.yml"
) else (
    echo [FAIL] No tunnel configuration found
    echo Run: setup_cloudflare_tunnel.bat
)

REM List tunnels
echo.
echo Available tunnels:
cloudflared.exe tunnel list

REM Check Windows service
echo.
echo Checking Windows service...
sc query Cloudflared >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [PASS] Cloudflare service installed
    sc query Cloudflared | findstr "RUNNING" >nul
    if %ERRORLEVEL% EQU 0 (
        echo [PASS] Service is running
    ) else (
        echo [INFO] Service is not running
        echo To start: net start Cloudflared
    )
) else (
    echo [INFO] Service not installed
    echo To install: cloudflared.exe service install
)

:end
echo.
echo Test complete!
pause
