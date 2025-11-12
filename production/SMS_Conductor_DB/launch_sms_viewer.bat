@echo off
REM Launch SMS Database Viewer with First Texts tab
cd /d "%~dp0"
echo.
echo ======================================
echo SMS DATABASE VIEWER
echo ======================================
echo.
echo Launching SMS viewer with First Texts tab...
echo - All 294 budtender messages loaded
echo - Ready for approval workflow
echo.
python SMSconductor_DB.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Failed to launch viewer
    pause
    exit /b %ERRORLEVEL%
)

