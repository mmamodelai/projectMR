@echo off
REM Create a SAFE, simple ZIP package for Spain
REM No Git, no scary stuff, just a clean zip file!

echo ========================================
echo  CREATING SAFE ZIP PACKAGE FOR SPAIN
echo ========================================
echo.

REM Create timestamp
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c%%a%%b)
for /f "tokens=1-2 delims=/: " %%a in ('time /t') do (set mytime=%%a%%b)
set TIMESTAMP=%mydate%_%mytime%

set PACKAGE_NAME=SMSConductorUI_Beta_v1.0_%TIMESTAMP%

echo Creating folder: %PACKAGE_NAME%
echo.

REM Create clean directory
if exist %PACKAGE_NAME% (
    rmdir /s /q %PACKAGE_NAME%
)
mkdir %PACKAGE_NAME%

echo [1/7] Copying main application...
copy conductor-sms\SMSconductor_DB.py %PACKAGE_NAME%\

echo [2/7] Copying launcher...
copy conductor-sms\START_SMS_VIEWER.bat %PACKAGE_NAME%\

echo [3/7] Copying requirements...
copy conductor-sms\requirements.txt %PACKAGE_NAME%\

echo [4/7] Copying SQL setup guide...
copy conductor-sms\CRITICAL_SQL_SETUP.md %PACKAGE_NAME%\

echo [5/7] Creating README...
(
echo SMS CONDUCTOR UI - BETA RELEASE v1.0
echo ====================================
echo.
echo QUICK START:
echo 1. Install Python 3.8+ from https://python.org
echo 2. Open command prompt here
echo 3. Run: pip install -r requirements.txt
echo 4. Double-click: START_SMS_VIEWER.bat
echo.
echo IMPORTANT FIRST-TIME SETUP:
echo Before using Schedule buttons, you MUST run the SQL setup.
echo See: CRITICAL_SQL_SETUP.md ^(takes 2 minutes^)
echo.
echo FEATURES:
echo - View all SMS messages
echo - Reply to customers
echo - Approve AI campaigns
echo - Schedule messages
echo - Live Mode ^(15-second auto-refresh with timestamp^)
echo - Always displays Pacific Time
echo.
echo SUPPORT:
echo Contact Luis for help: luis@motarewards.com
echo.
echo Version: Beta Release v1.0
echo Date: 2025-11-08
) > %PACKAGE_NAME%\README.txt

echo [6/7] Creating INSTALL_GUIDE...
(
echo INSTALLATION GUIDE - SMS Conductor UI
echo =====================================
echo.
echo STEP 1: Install Python
echo -----------------------
echo 1. Go to: https://python.org/downloads
echo 2. Download Python 3.8 or newer
echo 3. Run installer
echo 4. CHECK THE BOX: "Add Python to PATH"
echo 5. Click "Install Now"
echo.
echo STEP 2: Install Dependencies
echo ----------------------------
echo 1. Open Command Prompt in this folder
echo 2. Type: pip install -r requirements.txt
echo 3. Press Enter
echo 4. Wait for installation to complete
echo.
echo STEP 3: Run the Application
echo ---------------------------
echo Option A: Double-click START_SMS_VIEWER.bat
echo Option B: Double-click SMSconductor_DB.py
echo.
echo STEP 4: SQL Setup ^(FIRST TIME ONLY^)
echo ------------------------------------
echo 1. Open CRITICAL_SQL_SETUP.md
echo 2. Follow the 2-minute setup
echo 3. This enables the Schedule buttons
echo.
echo DONE! The application should now be running.
echo.
echo TROUBLESHOOTING:
echo - If Python not found: Reinstall Python with "Add to PATH" checked
echo - If dependencies fail: Try: python -m pip install --upgrade pip
echo - If database errors: Check internet connection
echo - If Schedule fails: Complete SQL setup in CRITICAL_SQL_SETUP.md
echo.
echo For help: Contact Luis
) > %PACKAGE_NAME%\INSTALL_GUIDE.txt

echo [7/7] Creating ZIP file...
powershell Compress-Archive -Path %PACKAGE_NAME% -DestinationPath %PACKAGE_NAME%.zip -Force

echo.
echo ========================================
echo  SUCCESS! PACKAGE CREATED
echo ========================================
echo.
echo ZIP File: %PACKAGE_NAME%.zip
echo Size: 
dir %PACKAGE_NAME%.zip | find ".zip"
echo.
echo WHAT'S INCLUDED:
echo - SMSconductor_DB.py ^(main application^)
echo - START_SMS_VIEWER.bat ^(easy launcher^)
echo - requirements.txt ^(Python dependencies^)
echo - CRITICAL_SQL_SETUP.md ^(SQL setup guide^)
echo - README.txt ^(quick start^)
echo - INSTALL_GUIDE.txt ^(detailed instructions^)
echo.
echo ========================================
echo  READY TO SEND TO SPAIN!
echo ========================================
echo.
echo Just send this ZIP file via:
echo - Email attachment
echo - Google Drive
echo - Dropbox
echo - WeTransfer
echo - Or any file sharing service
echo.
echo They unzip and follow README.txt!
echo.
echo ========================================
echo.
pause


