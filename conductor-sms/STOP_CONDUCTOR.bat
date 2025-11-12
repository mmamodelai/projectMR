@echo off
REM Kill any running Conductor processes
echo.
echo ================================================
echo STOPPING CONDUCTOR
echo ================================================
echo.

echo Searching for Conductor processes...
powershell -NoProfile -Command "$processes = Get-CimInstance Win32_Process | Where-Object {$_.CommandLine -like '*conductor_system.py*'}; if ($processes) { $processes | ForEach-Object { Write-Host \"  Killing PID $($_.ProcessId)...\"; Stop-Process -Id $_.ProcessId -Force }; Write-Host \"`n[OK] Conductor stopped`" } else { Write-Host \"[INFO] No Conductor process found\" }"

echo.
echo Waiting for COM port to release...
timeout /t 2 /nobreak >nul

echo.
echo [DONE] Conductor stopped
echo.
pause

