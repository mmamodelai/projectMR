@echo off
REM Deduplicate with TINY batches (for overloaded databases)
REM This is VERY SLOW but works when normal deduplication times out

cd /d "%~dp0"

echo ========================================
echo DEDUPLICATION - TINY BATCH MODE
echo ========================================
echo.
echo This uses VERY small batches (10 rows) with long waits (30s)
echo It will take HOURS/DAYS but works on overloaded databases.
echo.
echo Press Ctrl+C to stop safely at any time.
echo.
pause

python dedupe_blaze_tiny.py

pause

