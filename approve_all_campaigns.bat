@echo off
REM ================================================================
REM Bulk Approve Campaign Messages (SUG → APR)
REM ================================================================

echo ================================================================
echo BULK APPROVE CAMPAIGN MESSAGES
echo ================================================================
echo This will change all SUG messages to APR (approved)
echo After this, you can run the scheduler to assign send times
echo ================================================================
echo.

cd /d "%~dp0"
python approve_all_campaigns.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Approval failed with code %ERRORLEVEL%
    pause
    exit /b %ERRORLEVEL%
)

echo.
pause

