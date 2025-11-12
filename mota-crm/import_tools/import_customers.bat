@echo off
REM Import MoTa Customer Data to Supabase
REM Usage: import_customers.bat [--dry-run]

echo.
echo ========================================
echo MoTa Customer Data Import Tool
echo ========================================
echo.

cd /d "%~dp0"

REM Check if CSV file exists
if not exist "MEMBER_PERFORMANCE.csv" (
    echo ERROR: MEMBER_PERFORMANCE.csv not found!
    echo Please make sure the CSV file is in this directory.
    pause
    exit /b 1
)

REM Check if supabase package is installed
python -c "import supabase" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Installing required package: supabase...
    pip install supabase
    echo.
)

REM Run import script
if "%1"=="--dry-run" (
    echo Running in DRY RUN mode - no data will be written
    echo.
    python import_customers_to_supabase.py --dry-run
) else (
    echo WARNING: This will import/update customer data in Supabase
    echo Press Ctrl+C to cancel, or
    pause
    echo.
    python import_customers_to_supabase.py
)

echo.
if %ERRORLEVEL% EQU 0 (
    echo ========================================
    echo Import completed successfully!
    echo ========================================
) else (
    echo ========================================
    echo Import failed with errors
    echo ========================================
)

echo.
pause

