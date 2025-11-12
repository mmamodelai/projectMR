@echo off
REM Deduplicate with ULTRA-TINY batches (5 rows, 60s wait)
REM For SEVERELY overloaded databases

cd /d "%~dp0"

echo ========================================
echo DEDUPLICATION - ULTRA-TINY BATCH MODE
echo ========================================
echo.
echo This uses EXTREMELY small batches (5 rows) with long waits (60s)
echo It will take DAYS/WEEKS but works on severely overloaded databases.
echo.
echo BEFORE STARTING:
echo   1. Check if database is 'Healthy' in Supabase dashboard
echo   2. Consider deleting archive tables first
echo   3. This will run for DAYS - leave it running
echo.
echo Press Ctrl+C to stop safely at any time.
echo.
pause

python dedupe_blaze_ultra_tiny.py

pause

