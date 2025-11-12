@echo off
REM ================================================================
REM Update NEW Budtender Campaign Messages (Sept 18+ Signups)
REM Updates t-shirt welcome messages to 3-bubble format
REM ================================================================

echo ================================================================
echo UPDATE NEW BUDTENDER MESSAGES
echo ================================================================
echo Target: Sept 18, 2025 or later signups
echo Format: 3 bubbles (no "I'm excited for you")
echo ================================================================
echo.

cd /d "%~dp0"
python update_new_budtender_messages.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Update failed with code %ERRORLEVEL%
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ================================================================
echo SUCCESS: All NEW budtender messages updated!
echo Next: Check 'First Texts' tab in SMS Viewer
echo ================================================================
pause

