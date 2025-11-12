================================================================================
  SMS CONDUCTOR UI - MAC VERSION
  Beta Release v1.0
================================================================================

MAC-SPECIFIC INSTALLATION & USAGE GUIDE

================================================================================
  QUICK START (MAC)
================================================================================

OPTION 1: Auto-Launcher Script (Easiest)
------------------------------------------
1. Open Terminal (⌘ + Space → Type "Terminal" → Enter)
2. Navigate: cd [this folder]
3. Run: chmod +x START_SMS_VIEWER.sh
4. Run: ./START_SMS_VIEWER.sh
   OR
5. Double-click: START_SMS_VIEWER.sh in Finder
   (Click "Open" when macOS warns about untrusted file)

The script will:
- Check if Python 3 is installed
- Auto-install dependencies if missing
- Launch the application

OPTION 2: Manual Installation
------------------------------
1. Open Terminal (⌘ + Space → Type "Terminal" → Enter)
2. Navigate: cd [this folder]
3. Install dependencies:
   pip3 install -r requirements.txt
   (If that fails: python3 -m pip install -r requirements.txt)
4. Run application:
   python3 SMSconductor_DB.py

OPTION 3: AppleScript Launcher
------------------------------
1. Double-click: START_VIEWER_MAC.command
2. Application launches!

================================================================================
  FIRST-TIME SETUP (REQUIRED)
================================================================================

Before using Schedule buttons, you MUST complete SQL setup:

1. Open: CRITICAL_SQL_SETUP.md
2. Follow the 2-minute setup instructions
3. Deploy SQL functions to Supabase
4. Done! Schedule buttons will now work

================================================================================
  MAC-SPECIFIC FILES
================================================================================

LAUNCHERS:
----------
- START_SMS_VIEWER.sh           Main launcher (auto-installs deps)
- START_VIEWER_MAC.command      AppleScript launcher
- run_mac.sh                     Alternative launcher

DOCUMENTATION:
--------------
- MAC_INSTALLATION_GUIDE.md     Complete Mac setup guide
- MAC_QUICK_START.txt           Quick reference card

================================================================================
  INSTALLING PYTHON ON MAC
================================================================================

OPTION 1: Python.org (Recommended)
------------------------------------
1. Go to: https://www.python.org/downloads/
2. Download Python 3.8+ for macOS
3. Run installer
4. Check "Add Python to PATH" ✅
5. Done!

OPTION 2: Homebrew
------------------
1. Install Homebrew (if not installed):
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
2. Install Python:
   brew install python3
3. Done!

================================================================================
  SYSTEM REQUIREMENTS (MAC)
================================================================================

- macOS 10.14 (Mojave) or newer
- Python 3.8+ (install from python.org or Homebrew)
- Internet connection (required)
- 200MB disk space
- 4GB RAM (minimum)

================================================================================
  TROUBLESHOOTING (MAC)
================================================================================

"python3: command not found"
→ Install Python from python.org or: brew install python3

"pip3: command not found"
→ Use: python3 -m pip install -r requirements.txt

"Permission denied"
→ Use: pip3 install --user -r requirements.txt
→ Or: sudo pip3 install -r requirements.txt

"SSL Certificate Error"
→ Update certificates:
   /Applications/Python\ 3.x/Install\ Certificates.command
→ Or: pip3 install --upgrade certifi

"Tkinter not found"
→ Usually included, but if missing:
   brew install python-tk

"Script cannot be executed"
→ Make executable:
   chmod +x START_SMS_VIEWER.sh

================================================================================
  FEATURES
================================================================================

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

================================================================================
  ARCHITECTURE
================================================================================

SMS Viewer (Your Mac)
       ↓
Supabase Database (Cloud)
       ↑
Conductor (California)
       ↓
USB Modem → SMS Sent

Benefits:
✅ No modem needed on your computer
✅ Real-time sync across all users
✅ Centralized SMS sending (Conductor)
✅ Scalable (unlimited viewers)

================================================================================
  SUPPORT
================================================================================

Version: Beta Release v1.0
Platform: macOS 10.14+
Date: November 8, 2025

For support: Contact Luis

See also: MAC_INSTALLATION_GUIDE.md for detailed instructions

================================================================================
