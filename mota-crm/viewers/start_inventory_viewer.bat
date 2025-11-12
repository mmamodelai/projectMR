@echo off
REM Launch MoTa Inventory Viewer - NO TERMINAL

cd /d "%~dp0"
pip install supabase-py python-dotenv --upgrade >nul 2>&1
start "" pythonw.exe inventory_viewer_fixed.py
exit /b 0
