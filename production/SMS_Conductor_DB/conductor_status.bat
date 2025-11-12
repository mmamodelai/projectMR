@echo off
REM Simple Conductor Status Check
echo.
echo ================================================
echo CONDUCTOR SMS SYSTEM - STATUS CHECK
echo ================================================
echo.

cd /d "%~dp0"

REM Check for python process started from this directory
powershell -NoProfile -Command "Get-Process python* -ErrorAction SilentlyContinue | Where-Object {(Get-CimInstance Win32_Process -Filter \"ProcessId = $($_.Id)\").CommandLine -like '*conductor_system.py*'} | Select-Object Id, @{Name='Runtime';Expression={(Get-Date) - $_.StartTime}}, @{Name='MemoryMB';Expression={[math]::Round($_.WorkingSet64/1MB,0)}} | Format-Table -AutoSize"

if %ERRORLEVEL% EQU 0 (
    echo [STATUS] Conductor process found above
) else (
    echo [STATUS] Conductor NOT running
)

echo.
echo === CHECKING RECENT ACTIVITY ===
powershell -NoProfile -Command "$log = Get-Content 'logs\conductor_system.log' -Tail 3 -ErrorAction SilentlyContinue; if ($log) { $log | ForEach-Object { Write-Host $_ } } else { Write-Host '[ERROR] No log file found' }"

echo.
echo === CHECK MESSAGES IN DATABASE ===
echo Run: start_db_viewer.bat
echo Or check Supabase directly
echo.

pause
