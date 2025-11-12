@echo off
REM IC Viewer - BLAZE v3 (Proper 3-Panel Layout)
REM Features: Live-calculated fields, transaction drill-down, budtender info

echo Starting IC Viewer v3 (FIXED)...
cd /d "%~dp0"
python crm_integrated_blaze_v3.py
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Viewer failed to start
    pause
    exit /b %ERRORLEVEL%
)

