@echo off
REM Script: merge_duplicates.bat
REM Purpose: Run the duplicate customer merger
REM Part of: Conductor SMS System

echo ========================================
echo Duplicate Customer Merger
echo ========================================
echo.
echo This will merge duplicate customers in customers_blaze.
echo Press Ctrl+C to stop at any time.
echo.
pause

cd /d "%~dp0"
python merge_duplicates.py

echo.
echo ========================================
echo Merge Complete!
echo ========================================
pause

