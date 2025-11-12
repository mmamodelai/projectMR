@echo off
REM Fix Missing Product Names - Backfill from products_blaze

echo.
echo ================================================
echo   FIX MISSING PRODUCT NAMES
echo ================================================
echo.
echo This will backfill 582,435 missing product names
echo from the products_blaze table.
echo.
echo Takes about 10-15 minutes.
echo.
pause

python fix_missing_product_names_LOCAL.py

echo.
pause

