@echo off
REM IC Viewer v4 - ALL FIXES
REM - Column selectors for ALL panels (customers, transactions, items)
REM - Budtender name resolution (seller_id -> name)
REM - Fixed VIP calc (2-5=Casual, 6-14=Regular, 15+=VIP)
REM - Fixed Unknown brand filtering

echo Starting IC Viewer v4 (ALL FIXED)...
cd /d "%~dp0"
python crm_integrated_blaze_v4.py
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Viewer failed to start
    pause
    exit /b %ERRORLEVEL%
)

