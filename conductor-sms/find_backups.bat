@echo off
REM Find backup tables to delete

cd /d "%~dp0"

python find_backup_tables.py

pause

