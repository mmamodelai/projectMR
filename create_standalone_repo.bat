@echo off
REM Create standalone SMS Viewer repository

echo ========================================
echo  CREATING STANDALONE SMS VIEWER REPO
echo ========================================
echo.

REM Create directory
set REPO_NAME=sms-viewer-beta
if exist %REPO_NAME% (
    echo ERROR: Directory %REPO_NAME% already exists
    echo Please delete or rename it first
    pause
    exit /b 1
)

mkdir %REPO_NAME%
cd %REPO_NAME%

echo [1/6] Copying main application...
copy ..\conductor-sms\SMSconductor_DB.py .

echo [2/6] Copying dependencies...
copy ..\conductor-sms\requirements.txt .

echo [3/6] Copying launcher...
copy ..\conductor-sms\START_SMS_VIEWER.bat .

echo [4/6] Copying SQL setup guide...
copy ..\conductor-sms\CRITICAL_SQL_SETUP.md .

echo [5/6] Creating README...
(
echo # SMS Conductor - Beta Release v1.0
echo.
echo Professional SMS campaign management system with live updates and smart scheduling.
echo.
echo ## Quick Start
echo.
echo 1. Install Python 3.8+
echo 2. Run: `pip install supabase python-dateutil`
echo 3. Double-click: START_SMS_VIEWER.bat
echo.
echo ## IMPORTANT: SQL Setup
echo.
echo Before using Schedule buttons, see: CRITICAL_SQL_SETUP.md
echo.
echo ## Features
echo.
echo - View all messages in real-time
echo - Reply to customers
echo - Approve AI campaigns
echo - Schedule messages ^(flexible batch sizes^)
echo - Live Mode ^(15-second auto-refresh^)
echo - Always displays Pacific Standard Time
echo.
echo ## Version
echo.
echo Beta Release v1.0 - 2025-11-08
) > README.md

echo [6/6] Creating .gitignore...
(
echo __pycache__/
echo *.py[cod]
echo *.log
echo *.db
echo .vscode/
echo .idea/
echo config.json
) > .gitignore

echo.
echo ========================================
echo  STANDALONE REPO CREATED!
echo ========================================
echo.
echo Location: %cd%
echo.
echo Next steps:
echo 1. cd %REPO_NAME%
echo 2. git init
echo 3. git add .
echo 4. git commit -m "Initial commit - SMS Viewer Beta v1.0"
echo 5. gh repo create sms-viewer-beta --public --source=. --push
echo.
echo OR just zip this folder and send to Spain!
echo.
pause


