@echo off
REM ============================================================================
REM Import Leafly Data to Supabase
REM ============================================================================
REM Purpose: Run the Leafly data import script
REM Requires: Python, dependencies installed
REM ============================================================================

echo.
echo ============================================================================
echo LEAFLY DATA IMPORT TO SUPABASE
echo ============================================================================
echo.

cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found!
    echo Please install Python 3.7+ from python.org
    pause
    exit /b 1
)

REM Check if dependencies are installed
echo Checking dependencies...
python -c "import supabase" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Installing dependencies...
    pip install supabase fuzzywuzzy python-levenshtein
)

echo.
echo Starting import...
echo.

REM Run the import script
python import_leafly_data.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================================================
    echo IMPORT SUCCESSFUL!
    echo ============================================================================
) else (
    echo.
    echo ============================================================================
    echo IMPORT FAILED - Check error messages above
    echo ============================================================================
)

echo.
pause



