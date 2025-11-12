@echo off
REM Start Conductor in a NEW VISIBLE window
echo.
echo ================================================
echo STARTING CONDUCTOR (VISIBLE WINDOW)
echo ================================================
echo.

cd /d "%~dp0"

echo Starting Conductor in new window...
echo You will see a new Python window appear.
echo.
echo DO NOT CLOSE THIS WINDOW - Conductor will be in the other window.
echo.

REM Start in a NEW window with a clear title
start "CONDUCTOR SMS SYSTEM - DO NOT CLOSE" /D "%~dp0" python.exe conductor_system.py

echo.
echo [OK] Conductor started in new window
echo Look for: "CONDUCTOR SMS SYSTEM - DO NOT CLOSE"
echo.
echo To stop: Run STOP_CONDUCTOR.bat or close that window
echo.
timeout /t 3
exit

