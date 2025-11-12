@echo off
REM Import Transaction Data to Supabase
REM Part of Conductor SMS System

echo.
echo ========================================
echo Importing Transaction Data to Supabase
echo ========================================
echo.

cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python (python.org) and ensure it's added to your system PATH.
    echo.
    pause
    exit /b 1
)

REM Install dependencies if needed
echo Installing/upgrading Python dependencies...
pip install supabase --upgrade
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to install Python dependencies.
    echo Please check your internet connection or Python setup.
    echo.
    pause
    exit /b 1
)

REM Run the import script
echo.
echo Starting transaction data import...
echo This may take 30-60 minutes for 500,000+ records...
echo.
python "import_transaction_data.py" --batch-size 50
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo An error occurred during the import process.
    echo Please review the output above for details.
    echo.
    pause
    exit /b 1
) else (
    echo.
    echo Transaction data import completed successfully!
    echo.
    echo You can now:
    echo - View customer purchase history in CRM viewer
    echo - Query transactions by customer ID
    echo - Analyze product performance
    echo - Track staff performance
    echo.
)

echo Press any key to exit...
pause >nul
exit /b %ERRORLEVEL%
