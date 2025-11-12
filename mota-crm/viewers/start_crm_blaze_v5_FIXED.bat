@echo off
REM Start IC Viewer v5 - FIXED for NULL prices

echo.
echo ========================================
echo   IC VIEWER v5 - FIXED VERSION
echo ========================================
echo.
echo This version calculates prices from
echo unit_price x quantity when total_price
echo is NULL.
echo.

cd /d "%~dp0"
python crm_integrated_blaze_v5.py

pause

