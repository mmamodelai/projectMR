================================================================================
  SMS CONDUCTOR UI - WINDOWS VERSION
  Beta Release v1.0
================================================================================

WINDOWS-SPECIFIC INSTALLATION & USAGE GUIDE

================================================================================
  QUICK START (WINDOWS)
================================================================================

OPTION 1: Double-Click Launcher (Easiest)
------------------------------------------
1. Double-click: START_SMS_VIEWER.bat
2. Application launches!

OPTION 2: Standalone EXE (No Python Needed!)
---------------------------------------------
1. Double-click: SMSConductorDB_v1.1.exe
2. That's it! No Python installation required!

OPTION 3: Python Script
------------------------
1. Install Python 3.8+ from: https://www.python.org/downloads/
2. Check "Add Python to PATH" during installation
3. Double-click: SMSconductor_DB.py
   OR
4. Open Command Prompt, navigate here, run:
   python SMSconductor_DB.py

================================================================================
  FIRST-TIME SETUP (REQUIRED)
================================================================================

Before using Schedule buttons, you MUST complete SQL setup:

1. Open: CRITICAL_SQL_SETUP.md
2. Follow the 2-minute setup instructions
3. Deploy SQL functions to Supabase
4. Done! Schedule buttons will now work

================================================================================
  WINDOWS-SPECIFIC FILES
================================================================================

LAUNCHERS:
----------
- START_SMS_VIEWER.bat          Main launcher (recommended)
- start_SMSconductor_DB.bat     Alternative launcher
- launch_sms_viewer.bat         Another option

STANDALONE EXE:
---------------
- SMSConductorDB_v1.1.exe       Standalone executable (no Python needed!)

UTILITIES:
----------
- check_health.bat              Check system health
- conductor_status.bat         Check Conductor status
- modem_health.bat              Check modem status
- test_conductor.bat            Test SMS sending

================================================================================
  SYSTEM REQUIREMENTS (WINDOWS)
================================================================================

- Windows 10 or newer
- Python 3.8+ (unless using EXE)
- Internet connection (required)
- 200MB disk space
- 4GB RAM (minimum)

================================================================================
  TROUBLESHOOTING (WINDOWS)
================================================================================

"Python not found"
→ Install Python 3.8+ from python.org
→ Check "Add Python to PATH" during installation

"pip is not recognized"
→ Use: python -m pip install -r requirements.txt

"Windows Defender warning" (EXE only)
→ Click "More info" → "Run anyway"
→ This is normal with PyInstaller executables

"Module not found"
→ Run: pip install -r requirements.txt
→ Make sure you're in this folder when running

"Permission denied"
→ Right-click Command Prompt → "Run as Administrator"
→ Or install to user: pip install --user -r requirements.txt

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

SMS Viewer (Your Windows PC)
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
Platform: Windows 10/11
Date: November 8, 2025

For support: Contact Luis

================================================================================
