@echo off
REM Script: fix_com24.bat
REM Purpose: Pin modem to COM24 permanently
REM Part of: Conductor SMS System

echo.
echo ========================================
echo  MODEM COM24 FIX
echo ========================================
echo.
echo This will pin your modem to COM24 permanently
echo WARNING: Requires Administrator privileges!
echo.

REM Check if running as admin
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: This script requires Administrator privileges!
    echo.
    echo Please do ONE of the following:
    echo 1. Right-click Command Prompt and select "Run as Administrator"
    echo 2. Right-click this file and select "Run as Administrator"
    echo.
    pause
    exit /b 1
)

echo Running COM24 assignment script...
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "assign_com24.ps1"

if %ERRORLEVEL% EQ 0 (
    echo.
    echo ✓ Script completed successfully!
) else (
    echo.
    echo ERROR: Script failed with code %ERRORLEVEL%
)

pause



