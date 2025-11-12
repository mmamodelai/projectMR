@echo off
REM ================================================================
REM Campaign Scheduler - Preview (Dry Run)
REM Shows schedule without actually inserting into database
REM ================================================================

echo ================================================================
echo CAMPAIGN SCHEDULER - DRY RUN (PREVIEW ONLY)
echo ================================================================
echo This will show you the schedule without making any DB changes
echo ================================================================
echo.

cd /d "%~dp0"
python schedule_campaign.py --dry-run

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Preview failed with code %ERRORLEVEL%
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ================================================================
echo PREVIEW COMPLETE
echo Run schedule_campaign_now.bat to actually schedule these messages
echo ================================================================
pause

