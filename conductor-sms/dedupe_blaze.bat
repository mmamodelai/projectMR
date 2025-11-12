@echo off
REM Deduplicate Blaze tables using Supabase Python client
REM Bypasses SQL editor timeout

echo ========================================
echo BLAZE TABLES DEDUPLICATION
echo ========================================
echo.
echo Credentials: Hardcoded (ready to run)
echo Using: Supabase Python client (service role key)
echo.

REM Check if supabase is installed
python -c "import supabase" 2>nul
if errorlevel 1 (
    echo Installing supabase...
    pip install supabase
    if errorlevel 1 (
        echo ERROR: Failed to install supabase
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo STEP 1: CREATE SQL FUNCTIONS FIRST!
echo ========================================
echo.
echo You MUST create the SQL functions before running deduplication.
echo.
echo Run these 3 SQL files ONE AT A TIME in Supabase SQL Editor:
echo   1. sql_scripts\create_function_1_transaction_items.sql
echo   2. sql_scripts\create_function_2_products.sql
echo   3. sql_scripts\create_function_3_transactions.sql
echo.
echo See: sql_scripts\CREATE_FUNCTIONS_GUIDE.md for detailed instructions
echo.
echo Press any key to continue (or Ctrl+C to cancel and create functions first)...
pause >nul
echo.
echo ========================================
echo STEP 2: RUNNING DEDUPLICATION
echo ========================================
echo This may take 30+ minutes for millions of duplicates...
echo Progress will be shown below:
echo.
python dedupe_blaze_rpc.py

if errorlevel 1 (
    echo.
    echo ERROR: Script failed!
    echo Check the error message above.
    pause
    exit /b 1
)

echo.
echo ========================================
echo DEDUPLICATION COMPLETE
echo ========================================
echo.
echo Next steps:
echo 1. Run VACUUM ANALYZE in Supabase SQL Editor
echo 2. Check database size reduction
echo 3. Add unique indexes to prevent future duplicates
echo.
pause

