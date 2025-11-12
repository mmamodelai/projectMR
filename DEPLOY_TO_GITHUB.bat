@echo off
REM Deploy SMS Conductor UI to GitHub
REM Repository: https://github.com/mmamodelai/SMSConductorUI

echo ========================================
echo  DEPLOYING SMS CONDUCTOR UI TO GITHUB
echo ========================================
echo.
echo Repository: https://github.com/mmamodelai/SMSConductorUI
echo.

REM Create deployment directory
set DEPLOY_DIR=SMSConductorUI-deploy
if exist %DEPLOY_DIR% (
    echo Cleaning existing deployment directory...
    rmdir /s /q %DEPLOY_DIR%
)

mkdir %DEPLOY_DIR%
cd %DEPLOY_DIR%

echo [1/8] Copying main application...
copy ..\conductor-sms\SMSconductor_DB.py .

echo [2/8] Copying launcher...
copy ..\conductor-sms\START_SMS_VIEWER.bat .

echo [3/8] Copying requirements...
copy ..\conductor-sms\requirements.txt .

echo [4/8] Copying SQL setup guide...
copy ..\conductor-sms\CRITICAL_SQL_SETUP.md .

echo [5/8] Creating README.md...
(
echo # SMS Conductor UI - Beta Release v1.0
echo.
echo ^> Professional SMS campaign management system with live updates and smart scheduling.
echo.
echo ## 🚀 Quick Start
echo.
echo ### Requirements
echo - Python 3.8 or higher
echo - Internet connection ^(connects to Supabase^)
echo - Windows/Mac/Linux
echo.
echo ### Installation
echo.
echo 1. **Clone this repository**
echo    ```bash
echo    git clone https://github.com/mmamodelai/SMSConductorUI.git
echo    cd SMSConductorUI
echo    ```
echo.
echo 2. **Install dependencies**
echo    ```bash
echo    pip install -r requirements.txt
echo    ```
echo.
echo 3. **Run the application**
echo    ```bash
echo    # Windows:
echo    START_SMS_VIEWER.bat
echo    
echo    # Or double-click:
echo    SMSconductor_DB.py
echo    
echo    # Or command line:
echo    pythonw SMSconductor_DB.py
echo    ```
echo.
echo ### ⚠️ IMPORTANT: SQL Setup
echo.
echo **Before using Schedule buttons**, you must deploy SQL functions to Supabase.
echo.
echo See: `CRITICAL_SQL_SETUP.md` for step-by-step instructions ^(2 minutes^)
echo.
echo ---
echo.
echo ## ✨ Features
echo.
echo - 📥 **View all messages** in real-time
echo - 💬 **Reply to customers** manually
echo - ✅ **Approve AI campaigns** with feedback logging
echo - 📅 **Schedule campaigns** ^(flexible batch sizes^)
echo - 🔄 **Live Mode** ^(15-second auto-refresh^)
echo - 🎯 **Smart double-click** navigation
echo - 🌈 **Color-coded status** indicators
echo - 🕐 **Pacific Time display** ^(always PST, regardless of location^)
echo - 📊 **Pipeline visibility** ^(SUG → APR → SCH → sent^)
echo - ✔️ **Mark as read** functionality
echo.
echo ---
echo.
echo ## 📋 Tabs
echo.
echo 1. **All Messages** - Raw message history
echo 2. **Reply to Messages** - Unread inbox ^(right-click to mark read^)
echo 3. **First Texts** - Approve first contact messages
echo 4. **Campaign Master** - Complete pipeline view ^(all statuses^)
echo 5. **Approved** - Messages ready to schedule
echo 6. **Scheduled** - Timeline of upcoming sends
echo.
echo ---
echo.
echo ## 🎨 Key Features
echo.
echo ### Live Mode
echo Check the checkbox ^(top-right^) for 15-second auto-refresh
echo.
echo ### Smart Double-Click
echo - **Has conversation history** → Opens Reply tab ^(auto-selects^)
echo - **First contact** → Opens First Texts tab ^(highlights contact^)
echo.
echo ### Flexible Scheduling
echo - Type any number ^(e.g., `10`^) + click **Schedule**
echo - Or click **Schedule ALL** to queue everything
echo.
echo ### Mark as Read
echo - Right-click any conversation → **Mark as Read**
echo - Removes from Reply tab inbox
echo.
echo ### Color-Coded Status
echo - 🟡 Yellow = SUG ^(needs approval^)
echo - 🔵 Blue = APR ^(ready to schedule^)
echo - 🟢 Light Green = SCH ^(scheduled^)
echo - 🟢 Green = sent ^(delivered^)
echo.
echo ---
echo.
echo ## 🌐 Architecture
echo.
echo ```
echo SMS Viewer ^(Spain, anywhere^)
echo        ↓
echo Supabase Database ^(Cloud^)
echo        ↑
echo Conductor ^(California^)
echo        ↓
echo USB Modem → SMS Sent
echo ```
echo.
echo **Benefits:**
echo - ✅ No modem needed for SMS Viewer users
echo - ✅ Real-time sync across all users
echo - ✅ Centralized SMS sending ^(Conductor^)
echo - ✅ Scalable ^(unlimited viewers^)
echo.
echo ---
echo.
echo ## 🔧 Troubleshooting
echo.
echo ### "Could not find the function public.schedule_approved_messages"
echo - See `CRITICAL_SQL_SETUP.md`
echo - Must deploy SQL functions to Supabase ^(one-time setup^)
echo.
echo ### "Failed to open: 'SMSViewer' object has no attribute..."
echo - Update to latest version ^(v1.0+^)
echo - This was fixed in v1.0
echo.
echo ### Messages not sending
echo - Normal! SMS Viewer approves/schedules only
echo - Conductor ^(separate system^) sends messages
echo - Contact administrator if urgent
echo.
echo ### Database not loading
echo - Check internet connection
echo - Verify Supabase isn't down
echo - Click Refresh button
echo - Enable Live Mode
echo.
echo ---
echo.
echo ## 📦 Tech Stack
echo.
echo - **Python 3.8+**
echo - **Tkinter** ^(GUI^)
echo - **Supabase** ^(Database^)
echo - **PostgreSQL** ^(via Supabase^)
echo.
echo **Dependencies:**
echo - `supabase` - Database client
echo - `python-dateutil` - Timezone handling
echo.
echo ---
echo.
echo ## 📝 Version
echo.
echo **Beta Release v1.0** - 2025-11-08
echo.
echo **License:** Proprietary ^(custom software for client^)
echo.
echo **Support:** Contact Luis for issues/feedback
echo.
echo ---
echo.
echo ## 🚀 Future Enhancements ^(v1.1+^)
echo.
echo - Config file for credentials
echo - Built-in update checker
echo - Export campaign reports
echo - Custom scheduling rules per dispensary
echo - Dark mode
echo - Multi-language support
echo.
echo ---
echo.
echo **Built with ❤️ for professional SMS campaign management**
) > README.md

echo [6/8] Creating .gitignore...
(
echo # Python
echo __pycache__/
echo *.py[cod]
echo *$py.class
echo *.so
echo .Python
echo build/
echo develop-eggs/
echo dist/
echo downloads/
echo eggs/
echo .eggs/
echo lib/
echo lib64/
echo parts/
echo sdist/
echo var/
echo wheels/
echo *.egg-info/
echo .installed.cfg
echo *.egg
echo.
echo # Virtual Environment
echo venv/
echo ENV/
echo env/
echo.
echo # IDE
echo .vscode/
echo .idea/
echo *.swp
echo *.swo
echo *~
echo.
echo # OS
echo .DS_Store
echo Thumbs.db
echo.
echo # Logs
echo *.log
echo.
echo # Config
echo config.json
echo config.local.json
echo.
echo # Database
echo *.db
echo *.db-journal
echo.
echo # Temporary
echo *.tmp
echo *.bak
) > .gitignore

echo [7/8] Creating LICENSE...
(
echo MIT License
echo.
echo Copyright ^(c^) 2025 MOTA Rewards
echo.
echo Permission is hereby granted, free of charge, to any person obtaining a copy
echo of this software and associated documentation files ^(the "Software"^), to deal
echo in the Software without restriction, including without limitation the rights
echo to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
echo copies of the Software, and to permit persons to whom the Software is
echo furnished to do so, subject to the following conditions:
echo.
echo The above copyright notice and this permission notice shall be included in all
echo copies or substantial portions of the Software.
echo.
echo THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
echo IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
echo FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
echo AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
echo LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
echo OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
echo SOFTWARE.
) > LICENSE

echo [8/8] Initializing Git repository...
git init
git add .
git commit -m "Initial commit - SMS Conductor UI Beta v1.0"

echo.
echo ========================================
echo  READY TO PUSH!
echo ========================================
echo.
echo Repository structure created in: %cd%
echo.
echo **NEXT STEPS:**
echo.
echo 1. Add remote:
echo    git remote add origin https://github.com/mmamodelai/SMSConductorUI.git
echo.
echo 2. Push to GitHub:
echo    git push -u origin main
echo.
echo    ^(OR if branch is 'master'^):
echo    git push -u origin master
echo.
echo 3. Done! Share with Spain:
echo    https://github.com/mmamodelai/SMSConductorUI
echo.
echo ========================================
echo.
pause


