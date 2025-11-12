@echo off
REM Script: start_ic_viewer.bat
REM Purpose: Launch Enhanced IC Viewer v4 - Complete Customer Analytics
REM Updated: 2025-10-24 - Enhanced with expanded data views

echo.
echo ========================================
echo   ENHANCED IC VIEWER v4 - COMPLETE ANALYTICS
echo ========================================
echo.
echo Enhanced Customer Analytics Platform!
echo - EXPANDED Customer Data: IDs, Risk Analysis, Purchase Behavior
echo - DETAILED Transactions: Full timestamps, payment types, discounts, taxes
echo - COMPREHENSIVE Item Tracking: IDs, weights, pricing breakdown
echo - Revenue by Brand with category analysis
echo - Customer context and preferences
echo.

cd /d "%~dp0"
start "" pythonw.exe crm_integrated.py

echo.
echo ✅ IC Viewer launched!
echo.
