================================================================================
  SMS CONDUCTOR UI - PRODUCTION PACKAGE
  Beta Release v1.0
================================================================================

This folder contains the complete SMS Conductor UI application ready for
deployment to clients.

================================================================================
  QUICK START
================================================================================

WINDOWS:
--------
1. Double-click: START_SMS_VIEWER.bat
   OR
2. Double-click: SMSconductor_DB.py

MAC:
----
1. Open Terminal (⌘ + Space → Type "Terminal")
2. Navigate: cd [this folder]
3. Run: pip3 install -r requirements.txt
4. Run: python3 SMSconductor_DB.py
   OR
5. Double-click: START_SMS_VIEWER.sh

See: MAC_INSTALLATION_GUIDE.md for detailed Mac instructions

================================================================================
  FIRST-TIME SETUP (REQUIRED)
================================================================================

Before using Schedule buttons, you MUST complete SQL setup:

1. Open: CRITICAL_SQL_SETUP.md
2. Follow the 2-minute setup instructions
3. Deploy SQL functions to Supabase
4. Done! Schedule buttons will now work

================================================================================
  FILES INCLUDED
================================================================================

CORE APPLICATION:
-----------------
- SMSconductor_DB.py          Main application (2,900+ lines)
- START_SMS_VIEWER.bat         Windows launcher
- START_SMS_VIEWER.sh          Mac launcher (auto-installs dependencies)
- requirements.txt             Python dependencies

DOCUMENTATION:
--------------
- README.txt                   This file
- MAC_INSTALLATION_GUIDE.md    Complete Mac setup guide
- MAC_QUICK_START.txt          Quick Mac reference
- CRITICAL_SQL_SETUP.md        SQL function deployment (REQUIRED)
- DEPLOYMENT_OPTIONS.md        Deployment methods (ZIP, EXE, GitHub)
- SHIP_IT.md                   Complete shipping guide
- SHIP_TO_SPAIN.md             Spain-specific deployment
- EMAIL_TO_SPAIN.txt           Email template for client

FEATURES:
---------
✅ View all SMS messages in real-time
✅ Reply to customers manually
✅ Approve AI-generated campaigns
✅ Schedule messages (flexible batch sizes)
✅ Live Mode (15-second auto-refresh with timestamp)
✅ Smart double-click navigation
✅ Color-coded status indicators
✅ Always displays Pacific Standard Time (PST)
✅ Mark conversations as read
✅ Human-in-the-loop approval system
✅ Contact resolution (customers, budtenders, campaigns)

TABS:
-----
1. All Messages - Complete message history
2. Reply to Messages - Unread inbox (right-click to mark as read)
3. First Texts - Approve first contact messages
4. Campaign Master - Complete pipeline (SUG → APR → SCH → sent)
5. Approved - Messages ready to schedule
6. Scheduled - Timeline of upcoming sends

================================================================================
  SYSTEM REQUIREMENTS
================================================================================

WINDOWS:
--------
- Windows 10 or newer
- Python 3.8+ (or use standalone EXE - no Python needed)
- Internet connection (required)
- 200MB disk space
- 4GB RAM (minimum)

MAC:
----
- macOS 10.14 (Mojave) or newer
- Python 3.8+ (install from python.org or Homebrew)
- Internet connection (required)
- 200MB disk space
- 4GB RAM (minimum)

================================================================================
  DEPLOYMENT OPTIONS
================================================================================

OPTION 1: ZIP FILE (Simple)
---------------------------
- Send entire folder as ZIP
- Client extracts and runs START_SMS_VIEWER.bat (Windows) or START_SMS_VIEWER.sh (Mac)
- Requires Python installation

OPTION 2: STANDALONE EXE (Easiest for Windows)
-----------------------------------------------
- See: BUILD_EXE.bat (creates standalone EXE)
- No Python needed!
- Just double-click SMSConductor.exe
- ~62MB file size

OPTION 3: GITHUB REPOSITORY
----------------------------
- See: DEPLOY_TO_GITHUB.bat
- Professional Git repo
- Easy updates via git pull
- https://github.com/mmamodelai/SMSConductorUI

See: DEPLOYMENT_OPTIONS.md for complete comparison

================================================================================
  ARCHITECTURE
================================================================================

SMS Viewer (Client Computer)
       ↓
Supabase Database (Cloud)
       ↑
Conductor (California)
       ↓
USB Modem → SMS Sent

Benefits:
✅ No modem needed on client computer
✅ Real-time sync across all users
✅ Centralized SMS sending (Conductor)
✅ Scalable (unlimited viewers)

================================================================================
  TROUBLESHOOTING
================================================================================

WINDOWS:
--------
"Python not found"
→ Install Python 3.8+ from python.org
→ Check "Add Python to PATH" during installation

"Module not found"
→ Run: pip install -r requirements.txt

"Windows Defender warning" (EXE only)
→ Click "More info" → "Run anyway" (normal with PyInstaller)

MAC:
----
"python3: command not found"
→ Install Python from python.org or: brew install python3

"pip3: command not found"
→ Use: python3 -m pip install -r requirements.txt

"Permission denied"
→ Use: pip3 install --user -r requirements.txt

GENERAL:
--------
"Schedule button fails"
→ Complete SQL setup (see CRITICAL_SQL_SETUP.md)

"Database not loading"
→ Check internet connection
→ Verify Supabase isn't down
→ Click Refresh button
→ Enable Live Mode

"Messages not sending"
→ Normal! SMS Viewer approves/schedules only
→ Conductor (separate system) sends messages
→ Contact administrator if urgent

================================================================================
  SUPPORT
================================================================================

Version: Beta Release v1.0
Date: November 8, 2025
Status: Production Ready

For support: Contact Luis

================================================================================
  LICENSE
================================================================================

Proprietary - Custom software for client
Built with ❤️ for professional SMS campaign management

================================================================================
