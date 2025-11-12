@echo off
REM Script: start_ic_viewer.bat
REM Purpose: Launch IC Viewer - Internal Customer Viewer
REM Updated: 2025-10-23 - Renamed from CRM to IC Viewer

echo.
echo ========================================
echo   IC VIEWER - INTERNAL CUSTOMER SYSTEM
echo ========================================
echo.
echo Internal Customer Viewer with Revenue Analysis!
echo - Loads ALL customers with optimized queries
echo - Revenue by Brand breakdown
echo - Customer context and preferences
echo.

cd /d "%~dp0"
start "" pythonw.exe crm_integrated.py

echo.
echo ✅ IC Viewer launched!
echo.
