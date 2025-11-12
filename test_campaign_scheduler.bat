@echo off
REM Test Campaign Scheduler Functions
REM Checks business hours, schedules APR messages, processes SCH messages

echo.
echo ======================================================================
echo CAMPAIGN SCHEDULER TEST
echo ======================================================================
echo.

cd /d "%~dp0"
python test_campaign_scheduler.py

echo.
pause

