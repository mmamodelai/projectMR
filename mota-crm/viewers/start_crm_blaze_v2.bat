@echo off
REM IC Viewer - BLAZE v2 (Enhanced)
REM Features: Persistent settings, column selector, revenue analysis

echo Starting IC Viewer - BLAZE v2 (Enhanced Edition)...
cd /d "%~dp0"
python crm_integrated_blaze_v2.py
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Viewer failed to start
    pause
    exit /b %ERRORLEVEL%
)

