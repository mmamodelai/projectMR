@echo off
REM Kill and restart Conductor in visible window
title RESTART CONDUCTOR
color 0E

echo.
echo ================================================
echo    RESTART CONDUCTOR SMS SYSTEM
echo ================================================
echo.

cd /d "%~dp0"

REM Step 1: Stop any running Conductor
echo [1/3] Stopping any running Conductor...
powershell -NoProfile -Command "$processes = Get-CimInstance Win32_Process | Where-Object {$_.CommandLine -like '*conductor_system.py*'}; if ($processes) { $processes | ForEach-Object { Write-Host \"  Killing PID $($_.ProcessId)...\"; Stop-Process -Id $_.ProcessId -Force }; Write-Host \"`n[OK] Stopped\" } else { Write-Host \"[INFO] Not running\" }"

echo.
echo [2/3] Waiting for COM port...
timeout /t 3 /nobreak >nul

echo.
echo [3/3] Starting Conductor in NEW VISIBLE WINDOW...
echo.

REM Start in a NEW window with a clear title
start "⚡ CONDUCTOR SMS - LIVE" /D "%~dp0" cmd /k "color 0A && title ⚡ CONDUCTOR SMS SYSTEM - LIVE && python.exe conductor_system.py"

echo.
echo ================================================
echo    ✅ CONDUCTOR RESTARTED
echo ================================================
echo.
echo Look for window: "⚡ CONDUCTOR SMS - LIVE"
echo.
echo That window shows real-time message processing.
echo You can minimize it, but DON'T CLOSE IT.
echo.
echo To stop: Run STOP_CONDUCTOR.bat
echo          OR close the Conductor window
echo.
timeout /t 5
exit

