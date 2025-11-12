@echo off
REM Launch All MoTa Viewers - NO TERMINALS

cd /d "%~dp0"
pip install supabase-py python-dotenv --upgrade >nul 2>&1

echo Launching INTEGRATED CRM (Customer + Transactions + Items)...
start "" pythonw.exe crm_integrated.py

echo Launching Inventory Viewer...
start "" pythonw.exe inventory_viewer_fixed.py

exit /b 0