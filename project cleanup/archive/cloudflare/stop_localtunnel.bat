@echo off
REM Script: stop_localtunnel.bat
REM Purpose: Stop localtunnel
REM Part of: Conductor SMS System

echo ========================================
echo   Stopping Localtunnel
echo ========================================

REM Kill Node.js processes (localtunnel)
taskkill /f /im node.exe 2>nul

if %ERRORLEVEL% EQU 0 (
    echo Localtunnel stopped successfully!
) else (
    echo No localtunnel processes found.
)

echo.
pause
