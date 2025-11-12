@echo off
REM OliverSelector Customer Simulator Launcher
REM Part of Conductor SMS System

echo Starting OliverSelector Customer Simulator...
cd /d "%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Install dependencies if needed
echo Installing dependencies...
pip install -r requirements.txt

REM Run the simulator
echo Launching Customer Simulator...
python customer_simulator.py

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Simulator failed to start
    pause
    exit /b %ERRORLEVEL%
)

echo Simulator closed successfully
pause
