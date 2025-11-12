@echo off
REM Find LARGE backup tables (not tiny API samples)

cd /d "%~dp0"

python find_large_backup_tables.py

pause

