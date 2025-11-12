@echo off
REM Deduplicate with MEDIUM batches (250 rows)
REM For databases that timeout on 1000-row batches

cd /d "%~dp0"

echo ========================================
echo DEDUPLICATION - MEDIUM BATCH MODE
echo ========================================
echo.
echo Using 250-row batches (smaller than normal, faster than tiny)
echo Expected: 2-4 hours for millions of duplicates
echo.
pause

python dedupe_blaze_medium.py

pause

