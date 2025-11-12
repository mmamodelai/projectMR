@echo off
REM Quick database health check

cd /d "%~dp0"

python check_db_health.py

pause

