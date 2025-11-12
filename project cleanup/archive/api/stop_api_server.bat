@echo off
REM Script: stop_api_server.bat
REM Purpose: Stop the API server
REM Part of: Conductor SMS System

echo ========================================
echo   Stopping Conductor API Server
echo ========================================

REM Kill Python processes (API server)
taskkill /f /im python.exe 2>nul

if %ERRORLEVEL% EQU 0 (
    echo API Server stopped successfully!
) else (
    echo No API server processes found.
)

echo.
pause
