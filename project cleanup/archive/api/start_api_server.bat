@echo off
REM Script: start_api_server.bat
REM Purpose: Start the API server for n8n integration
REM Part of: Conductor SMS System

echo ========================================
echo   Starting Conductor API Server
echo ========================================
echo Starting API server on port 5001...
echo This will run in the background.
echo ========================================

cd /d "%~dp0"

REM Kill any existing Python processes that might be running the API server
taskkill /f /im python.exe 2>nul

REM Start the API server
start "Conductor API Server" /min python api_server.py

echo API Server started successfully!
echo.
echo The API server is now running on: http://localhost:5001
echo.
echo To stop the server, run: stop_api_server.bat
echo.
pause