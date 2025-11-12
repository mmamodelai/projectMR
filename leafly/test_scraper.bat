@echo off
REM Script: test_scraper.bat
REM Purpose: Test the Leafly scraper
REM Part of: Conductor SMS System - Leafly Scraper

echo.
echo ========================================
echo   Testing Leafly Scraper
echo ========================================
echo.

cd /d "%~dp0"

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate" (
    call venv\Scripts\activate
)

python test_scraper.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Tests failed
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ✅ All tests passed!
pause

