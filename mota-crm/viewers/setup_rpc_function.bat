@echo off
REM ==========================================
REM Setup RPC Function for IC Viewer v5.5
REM ==========================================
REM 
REM This script creates the get_customers_fast()
REM function in Supabase so the viewer can use
REM FAST MODE instead of fallback mode.
REM
REM Run time: ~10-15 minutes (one time only!)
REM
REM ==========================================

echo.
echo ========================================
echo   IC VIEWER v5.5 - RPC SETUP
echo ========================================
echo.
echo This will:
echo   1. Backfill customer stats (~10-15 min)
echo   2. Create RPC function (instant)
echo.
echo You only need to run this ONCE!
echo.
pause

cd /d "%~dp0"
python setup_rpc_function.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Setup failed
    echo Error code: %ERRORLEVEL%
    echo.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ========================================
echo   SETUP COMPLETE!
echo ========================================
echo.
echo Now restart the IC Viewer!
echo.
pause

