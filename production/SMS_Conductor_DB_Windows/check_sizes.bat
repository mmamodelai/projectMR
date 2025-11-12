@echo off
REM Check table sizes to identify what's taking up space

cd /d "%~dp0"

python check_table_sizes.py

pause

