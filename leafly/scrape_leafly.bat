@echo off
REM Script: scrape_leafly.bat
REM Purpose: Scrape strain data from Leafly
REM Part of: Conductor SMS System - Leafly Scraper

echo.
echo ========================================
echo   Leafly Strain Scraper
echo ========================================
echo.

if "%~1"=="" (
    echo Usage:
    echo   scrape_leafly.bat "Gelato 41"
    echo   scrape_leafly.bat --batch strains.txt
    echo   scrape_leafly.bat --url "https://www.leafly.com/strains/gelato-41"
    echo.
    pause
    exit /b 1
)

cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate
    pip install -r requirements_scraper.txt
) else (
    call venv\Scripts\activate
)

REM Run scraper
python leafly_scraper.py %*

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ ERROR: Scraper failed with code %ERRORLEVEL%
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ✅ Scraping complete!
pause

