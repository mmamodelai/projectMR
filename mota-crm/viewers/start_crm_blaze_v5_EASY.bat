@echo off
REM IC Viewer v5 - EASY SETUP
REM This will guide you through the setup

echo ========================================
echo IC VIEWER V5 - EASY SETUP
echo ========================================
echo.
echo This script will help you set up v5!
echo.
echo OPTION 1: Automated (Slower)
echo   - Run setup_viewer_v5.py
echo   - Takes 30-60 minutes
echo   - Works via API
echo.
echo OPTION 2: Manual (FASTER - Recommended!)
echo   - Open Supabase SQL Editor
echo   - Copy/paste 2 SQL files
echo   - Takes 11-16 minutes total
echo.
echo Which do you prefer?
echo [1] Automated (slow but easy)
echo [2] Manual (FAST - I'll do it myself)
echo.
choice /C 12 /N /M "Choose: "

if %ERRORLEVEL%==1 (
    echo.
    echo Starting automated setup...
    python setup_viewer_v5.py
    pause
    goto launch
)

if %ERRORLEVEL%==2 (
    echo.
    echo Great! Here's what to do:
    echo.
    echo 1. Open: https://supabase.com/dashboard/project/kiwmwoqrguyrcpjytgte/sql
    echo.
    echo 2. In SQL Editor, run THIS file:
    echo    sql_scripts\HYBRID_SOLUTION_step1_backfill.sql
    echo    (Wait 10-15 minutes)
    echo.
    echo 3. Then run THIS file:
    echo    sql_scripts\HYBRID_SOLUTION_step2_create_fast_query.sql
    echo    (Wait 1 minute)
    echo.
    echo 4. Come back here and press any key to launch viewer!
    echo.
    pause
    goto launch
)

:launch
echo.
echo Launching IC Viewer v5...
echo.
python crm_integrated_blaze_v5.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Viewer failed to start
    echo Check error message above
    pause
)

