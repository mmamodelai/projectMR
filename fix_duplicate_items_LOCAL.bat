@echo off
REM Fix Duplicate Transaction Items - Local Version
REM This connects directly to Supabase (no timeout!)

echo.
echo ========================================
echo   Fix Duplicate Items - Local Version
echo ========================================
echo.
echo This will connect directly to Supabase
echo and remove 1.2M duplicate items.
echo.
echo You will need your Supabase database password.
echo (Find it in: Supabase Dashboard -^> Settings -^> Database)
echo.
pause

python fix_duplicate_items_LOCAL.py

echo.
pause



