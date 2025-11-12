@echo off
REM Script: test_conductor.bat
REM Purpose: Send test SMS via Conductor System
REM Part of: Conductor SMS System

echo ========================================
echo   CONDUCTOR SMS SYSTEM v2.0
echo   Test Message Sender
echo ========================================
echo.

cd /d "%~dp0"

if "%~2"=="" (
    echo Usage: test_conductor.bat ^<phone_number^> ^<message^>
    echo.
    echo Example:
    echo   test_conductor.bat +16199773020 "Test message"
    echo.
    pause
    exit /b 1
)

python conductor_system.py test %*

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Failed to queue message
    pause
    exit /b %ERRORLEVEL%
)

pause

