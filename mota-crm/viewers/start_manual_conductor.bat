@echo off
REM Manual Conductor - SMS Conversation Manager
REM Similar to IC Viewer but for SMS

echo ========================================
echo MANUAL CONDUCTOR - SMS Manager
echo ========================================
echo.
echo Features:
echo - View conversations with unread indicators
echo - Full conversation threads
echo - Customer details from CRM
echo - Quick reply
echo - Mark as read/unread
echo.
echo Starting...
echo.

cd /d "%~dp0"
python manual_conductor.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Manual Conductor failed to start
    echo Check error message above
    pause
)

