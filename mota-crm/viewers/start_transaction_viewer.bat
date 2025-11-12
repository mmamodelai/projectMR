@echo off
REM Launch MoTa Transaction Viewer - NO TERMINAL

cd /d "%~dp0"
pip install supabase-py python-dotenv --upgrade >nul 2>&1
start "" pythonw.exe transaction_viewer_enhanced.py
exit /b 0