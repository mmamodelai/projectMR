@echo off
REM Script: detect_modem.bat
REM Purpose: Auto-detect modem port and restart Conductor
REM Part of: Conductor SMS System

echo.
echo ========================================
echo  AUTO-DETECT MODEM PORT
echo ========================================
echo.

cd /d "%~dp0"

echo Step 1: Finding modem...
python auto_detect_modem.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Could not auto-detect modem!
    echo.
    echo Please check:
    echo 1. Is your modem connected via USB?
    echo 2. Are the device drivers installed?
    echo 3. Try manually assigning COM24 using Device Manager
    echo.
    pause
    exit /b 1
)

echo.
echo Step 2: Restarting Conductor...
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak
echo.
call start_conductor.bat

pause



