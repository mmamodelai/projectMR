@echo off
REM IC Viewer v5 - HYBRID (Server-Side RPC)
REM Requires: HYBRID_SOLUTION SQL scripts run first

echo ========================================
echo IC Viewer v5 - HYBRID MODE
echo ========================================
echo.
echo PREREQUISITES:
echo 1. Run: HYBRID_SOLUTION_step1_backfill.sql (fills visits/lifetime)
echo 2. Run: HYBRID_SOLUTION_step2_create_fast_query.sql (creates RPC function)
echo.
echo Starting viewer...
echo.

cd /d "%~dp0"
python crm_integrated_blaze_v5.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Viewer failed to start
    pause
    exit /b %ERRORLEVEL%
)

