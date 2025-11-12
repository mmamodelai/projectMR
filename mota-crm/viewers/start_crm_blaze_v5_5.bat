@echo off
REM ==========================================
REM IC VIEWER v5.5 - REDESIGNED
REM ==========================================
REM 
REM Launch script for the redesigned IC Viewer
REM 
REM Features:
REM - Narrower transactions panel
REM - WIDER baseball card (700px)
REM - Visit frequency analytics
REM - Top 5 brands in baseball card
REM - Column visibility toggle (Display menu)
REM 
REM ==========================================

echo.
echo ========================================
echo   IC VIEWER v5.5 - REDESIGNED
echo ========================================
echo.
echo Starting viewer...
echo.

cd /d "%~dp0"
python crm_integrated_blaze_v5_5.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Failed to start viewer
    echo Error code: %ERRORLEVEL%
    echo.
    pause
    exit /b %ERRORLEVEL%
)

pause

