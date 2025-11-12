@echo off
REM Sync transactions from Blaze API to Supabase

cd /d "%~dp0"

echo ========================================
echo BLAZE API TRANSACTION SYNC
echo ========================================
echo.
echo This will fetch transactions from Blaze API
echo and UPSERT them to Supabase (no duplicates)
echo.
pause

python blaze_sync_transactions.py 7

pause

