@echo off
REM Quick check: Is Conductor running?
echo.
echo Checking for Conductor...
echo.

powershell -Command "Get-CimInstance Win32_Process | Where-Object {$_.CommandLine -like '*conductor_system.py*'} | Select-Object ProcessId, @{Name='Runtime';Expression={(Get-Date) - $_.CreationDate}}, CommandLine | Format-List"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [OK] Found Conductor process above
    echo.
    echo To see real-time logs:
    echo    Get-Content logs\conductor_system.log -Tail 20 -Wait
    echo.
) else (
    echo [NOT FOUND] Conductor is not running
    echo.
    echo To start: python conductor_system.py
    echo.
)
pause

