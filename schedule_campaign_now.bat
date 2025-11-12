@echo off
REM ================================================================
REM Campaign Scheduler - LIVE (Actual Scheduling)
REM Schedules campaign messages with random 4-7 min intervals
REM ================================================================

echo ================================================================
echo CAMPAIGN SCHEDULER - LIVE MODE
echo ================================================================
echo WARNING: This will schedule messages for sending!
echo ================================================================
echo.
echo Settings:
echo - Random intervals: 4-7 minutes
echo - Human skips: 15-20%% chance of extra 10-15 min delay
echo - Business hours: 9 AM - 8 PM
echo - Respects weekends
echo.
echo ================================================================
echo.

set /p CONFIRM="Type YES to confirm scheduling: "
if /I not "%CONFIRM%"=="YES" (
    echo.
    echo Cancelled by user
    pause
    exit /b 1
)

echo.
echo Scheduling messages...
echo.

cd /d "%~dp0"
python schedule_campaign.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Scheduling failed with code %ERRORLEVEL%
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ================================================================
echo SCHEDULING COMPLETE!
echo.
echo Messages are now in scheduled_messages table
echo Conductor will auto-send them at their scheduled times
echo.
echo To cancel: UPDATE scheduled_messages SET status='cancelled' WHERE id=X
echo To monitor: SELECT * FROM scheduled_messages WHERE status='scheduled'
echo ================================================================
pause

