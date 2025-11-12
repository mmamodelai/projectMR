@echo off
REM Update OLD budtender messages (9/14/2025 and earlier)
REM Changes t-shirt welcome to joints/product feedback message

cd /d "%~dp0"

echo.
echo ======================================================================
echo UPDATE OLD BUDTENDER CAMPAIGN MESSAGES
echo ======================================================================
echo.
echo Cutoff Date: September 14, 2025
echo  - ON OR BEFORE 9/14/2025: Get NEW joints/feedback message
echo  - AFTER 9/14/2025: Keep ORIGINAL t-shirt welcome message
echo.
echo This will update the database. Press Ctrl+C to cancel.
echo.
pause

python update_old_budtender_messages.py

echo.
echo ======================================================================
echo DONE! Check results above.
echo ======================================================================
echo.
pause

