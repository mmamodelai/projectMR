@echo off
REM SMS Conductor - Beta Release v1.0
REM Start the SMS Viewer

echo ========================================
echo  SMS CONDUCTOR - BETA RELEASE v1.0
echo ========================================
echo.
echo Starting SMS Viewer...
echo.

cd /d "%~dp0"
pythonw SMSconductor_DB.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Failed to start SMS Viewer
    echo.
    echo TROUBLESHOOTING:
    echo 1. Make sure Python 3.8+ is installed
    echo 2. Run: pip install supabase python-dateutil
    echo 3. Contact Luis if issues persist
    echo.
    pause
    exit /b %ERRORLEVEL%
)


