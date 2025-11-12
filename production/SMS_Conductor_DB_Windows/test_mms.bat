@echo off
REM Test MMS Sending
REM Stops conductor, sends MMS, then restarts conductor

echo.
echo ========================================
echo MMS TEST SCRIPT
echo ========================================
echo.
echo This will:
echo 1. Stop Conductor (to free COM port)
echo 2. Send test MMS message
echo 3. Restart Conductor
echo.
pause

echo.
echo [1/3] Stopping Conductor...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Conductor*" 2>nul
timeout /t 2 /nobreak >nul

echo.
echo [2/3] Sending MMS...
cd /d "%~dp0"
python send_mms_test.py

echo.
echo [3/3] Restarting Conductor in new window...
start "Conductor SMS" cmd /k python conductor_system.py

echo.
echo ========================================
echo Done! Check your phone for the MMS.
echo ========================================
echo.
pause


