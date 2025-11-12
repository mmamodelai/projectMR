@echo off
REM ============================================
REM SMS Conductor Database Viewer - Build EXE
REM ============================================

echo.
echo ================================================
echo  SMS Conductor Database Viewer - Build Script
echo ================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found!
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

echo Checking PyInstaller...
python -c "import PyInstaller" >nul 2>&1
if %errorlevel% neq 0 (
    echo PyInstaller not found. Installing...
    python -m pip install pyinstaller
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install PyInstaller
        pause
        exit /b 1
    )
    echo PyInstaller installed successfully!
)

echo.
echo Building EXE...
echo.

REM Run the build script
python conductor-sms\build_exe.py

if %errorlevel% equ 0 (
    echo.
    echo ================================================
    echo  BUILD COMPLETE!
    echo ================================================
    echo.
    echo Output: dist\SMSConductorDB\SMSConductorDB.exe
    echo.
    echo To distribute:
    echo   1. Zip the entire "dist\SMSConductorDB" folder
    echo   2. Share the zip file
    echo   3. Users extract and run SMSConductorDB.exe
    echo.
) else (
    echo.
    echo ================================================
    echo  BUILD FAILED!
    echo ================================================
    echo.
    echo Check the error messages above.
    echo.
)

pause
