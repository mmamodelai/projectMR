@echo off
REM Script: get_sales_data.bat
REM Purpose: Fetch sales data for specific dates
REM Part of: Conductor SMS System

echo.
echo ==========================================
echo   SALES DATA REPORT GENERATOR
echo ==========================================
echo.
echo Fetching sales data for:
echo   - Sept 25, 2025
echo   - Oct 25, 2025
echo   - Nov 1-5, 2025
echo   - Dec 24, 2024
echo.

REM Check if pandas is installed
python -c "import pandas" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Installing required packages...
    pip install pandas tabulate supabase
    echo.
)

REM Run the script
python get_sales_data.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Script failed with code %ERRORLEVEL%
    echo.
)

pause



