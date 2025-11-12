@echo off
REM Script: check_duplicates.bat
REM Purpose: Check current duplicate status
REM Part of: Conductor SMS System

cd /d "%~dp0"
python check_duplicates.py

