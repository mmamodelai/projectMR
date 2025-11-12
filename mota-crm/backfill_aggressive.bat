@echo off
REM AGGRESSIVE Backfill - Jan 1, 2024

cd /d "%~dp0"

echo ========================================
echo AGGRESSIVE BACKFILL
echo ========================================
echo.
echo Settings:
echo   - 7,500 API calls per 5 min (safe margin)
echo   - 500 items per UPSERT batch
echo   - 7-day windows
echo   - Start: Jan 1, 2020
echo.
echo This will be MUCH FASTER than the old script.
echo Expected: 2-4 hours for all transactions.
echo.
pause

python backfill_aggressive.py

pause

