@echo off
REM Script: start_crm_optimized.bat
REM Purpose: Launch OPTIMIZED CRM viewer (uses new Supabase views)
REM Version: 2.0 with customer_sms_context

echo.
echo ========================================
echo   MoTa CRM - OPTIMIZED (v2)
echo ========================================
echo.
echo Using new Supabase views for 10-50x speed boost!
echo.

cd /d "%~dp0"
start "" pythonw crm_integrated_v2.py

echo.
echo ✅ Optimized CRM viewer launched!
echo.
echo Features:
echo   - customer_sms_context view (1 query vs 5)
echo   - Cascading queries (only load what's needed)
echo   - Performance tracking (see query times)
echo.

