@echo off
REM Backfill transaction items from Jan 1, 2024

cd /d "%~dp0"

echo ========================================
echo BACKFILL FROM JAN 1, 2024
echo ========================================
echo.
echo This will fetch ALL transactions from Jan 1, 2024 to now
echo Processing in 7-day windows (Blaze API requirement)
echo Using UPSERT (no duplicates)
echo.
echo This may take several hours for $19M in transactions.
echo Press Ctrl+C to stop safely at any time.
echo.
pause

python backfill_from_jan_2024.py

pause

