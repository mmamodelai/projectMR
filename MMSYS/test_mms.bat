@echo off
REM Test MMS Sending
REM Sends long test message to 619-977-3020

echo.
echo ========================================
echo MMS TEST - Long Message as Single Bubble
echo ========================================
echo.
echo This will send an 827-character message
echo as ONE MMS bubble (not 6 SMS bubbles)
echo.
echo IMPORTANT: Make sure Conductor is STOPPED
echo           (to free COM24 port)
echo.
pause

cd /d "%~dp0"
python test_mms.py

echo.
pause


