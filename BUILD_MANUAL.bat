@echo off
REM ============================================
REM SMS Conductor DB - Manual PyInstaller Build
REM (Alternative if build_exe.py doesn't work)
REM ============================================

echo.
echo Building SMS Conductor Database Viewer...
echo.

REM Direct PyInstaller command
python -m PyInstaller --clean --noconfirm SMSConductorDB.spec

if %errorlevel% equ 0 (
    echo.
    echo ================================================
    echo  BUILD COMPLETE!
    echo ================================================
    echo.
    echo Output: dist\SMSConductorDB\SMSConductorDB.exe
    echo.
) else (
    echo.
    echo ================================================
    echo  BUILD FAILED!
    echo ================================================
    echo.
    echo Try installing PyInstaller manually:
    echo   python -m pip install pyinstaller
    echo.
)

pause

