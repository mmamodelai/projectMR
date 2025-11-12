# SMS Conductor - Deployment Guide

## 🚀 How to Package for Distribution (Spain, etc.)

---

## **OPTION 1: Standalone Executable (Recommended for Non-Technical Users)**

### **Step 1: Install PyInstaller**
```bash
pip install pyinstaller
```

### **Step 2: Create Executable**
```bash
cd C:\Dev\conductor\conductor-sms
pyinstaller --onefile --windowed --name "SMS_Conductor" SMSconductor_DB.py
```

**This creates:**
- `dist/SMS_Conductor.exe` - Standalone executable (no Python installation needed!)

### **Step 3: Package for Distribution**

Create a folder with:
```
SMS_Conductor_Package/
├── SMS_Conductor.exe          # The executable
├── config.json                 # Supabase credentials (see below)
└── README_INSTALL.txt          # Installation instructions
```

**config.json example:**
```json
{
  "supabase_url": "https://kiwmwoqrguyrcpjytgte.supabase.co",
  "supabase_key": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "crm_url": "https://kiwmwoqrguyrcpjytgte.supabase.co",
  "crm_key": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**README_INSTALL.txt:**
```
SMS CONDUCTOR - INSTALLATION
============================

1. Double-click SMS_Conductor.exe
2. That's it!

REQUIREMENTS:
- Windows 10/11
- Internet connection (for Supabase)

SUPPORT:
Contact Luis if you have any issues.
```

---

## **OPTION 2: Python Installation (For Technical Users)**

### **Step 1: Install Python 3.8+**
Download from: https://www.python.org/downloads/

### **Step 2: Install Dependencies**
```bash
cd conductor-sms
pip install -r requirements.txt
```

### **Step 3: Run**
```bash
pythonw SMSconductor_DB.py
```

**OR create a shortcut:**
- Right-click `SMSconductor_DB.py`
- Create shortcut
- Edit shortcut target to: `pythonw "C:\path\to\SMSconductor_DB.py"`

---

## **CURRENT STATUS: What's Ready vs. What's Needed**

### ✅ **READY NOW:**
1. **SMS Database Viewer** - 100% ready
   - All tabs working
   - Live mode (15s refresh)
   - Mark as read
   - Campaign Master view
   - Flexible scheduling

2. **Supabase Integration** - 100% ready
   - All functions deployed
   - Credentials hardcoded (needs config file)

3. **Core Functionality** - 100% ready
   - View messages
   - Reply to messages
   - Approve campaigns
   - Schedule campaigns
   - Double-click to open

### ⚠️ **NEEDS WORK:**
1. **Credentials Management** - CRITICAL
   - Currently hardcoded in `SMSconductor_DB.py`
   - Need to move to external `config.json`
   - Or use environment variables
   - **STATUS**: 30 minutes of work

2. **PyInstaller Build** - NOT TESTED YET
   - Need to test executable creation
   - May need icon file
   - **STATUS**: 1 hour to test and fix issues

3. **Conductor System (Modem)** - LOCATION-SPECIFIC
   - Requires USB modem on each machine
   - Requires COM port configuration
   - **STATUS**: Works on your machine, needs testing on Spain machine

---

## **TO MAKE IT DISTRIBUTABLE (Checklist):**

### **CRITICAL (Must Do Before Spain):**
- [ ] Move Supabase credentials to `config.json`
- [ ] Update code to read from `config.json`
- [ ] Test PyInstaller build
- [ ] Create installer package with README

### **NICE TO HAVE:**
- [ ] Add app icon
- [ ] Create installer wizard (NSIS or Inno Setup)
- [ ] Auto-update mechanism
- [ ] Error logging to file
- [ ] "First run" setup wizard

---

## **FIXING CREDENTIALS (Step-by-Step)**

### **Current Problem:**
Supabase keys are hardcoded in lines 22-36 of `SMSconductor_DB.py`

### **Solution:**

**1. Create config.json template:**
```json
{
  "supabase": {
    "url": "https://kiwmwoqrguyrcpjytgte.supabase.co",
    "key": "your_anon_key_here"
  },
  "crm": {
    "url": "https://kiwmwoqrguyrcpjytgte.supabase.co",
    "key": "your_anon_key_here"
  }
}
```

**2. Update SMSconductor_DB.py:**
```python
import json
import os

# Load config
config_path = os.path.join(os.path.dirname(__file__), 'config.json')
with open(config_path, 'r') as f:
    config = json.load(f)

SUPABASE_URL = config['supabase']['url']
SUPABASE_KEY = config['supabase']['key']
CRM_URL = config['crm']['url']
CRM_KEY = config['crm']['key']
```

**3. Add config.json to .gitignore:**
```
config.json
```

**4. Create config.example.json for distribution:**
```json
{
  "supabase": {
    "url": "https://YOUR_PROJECT.supabase.co",
    "key": "YOUR_ANON_KEY"
  },
  "crm": {
    "url": "https://YOUR_PROJECT.supabase.co",
    "key": "YOUR_ANON_KEY"
  }
}
```

---

## **TESTING CHECKLIST (Before Spain):**

### **On Your Machine:**
- [ ] Run SMS Viewer from Python
- [ ] Enable Live Mode - verify 15s refresh
- [ ] Schedule messages - verify they appear
- [ ] Mark as read - verify they disappear
- [ ] Build executable with PyInstaller
- [ ] Test executable (double-click to run)

### **On Test Machine (NOT Spain):**
- [ ] Copy executable + config.json
- [ ] Double-click executable
- [ ] Verify it connects to Supabase
- [ ] Verify all tabs load
- [ ] Schedule a test message

### **On Spain Machine:**
- [ ] Copy executable + config.json
- [ ] Test SMS Viewer
- [ ] Install modem drivers (if needed)
- [ ] Configure COM port
- [ ] Test full workflow

---

## **ESTIMATED TIME TO PRODUCTION-READY:**

### **For SMS Viewer ONLY (no modem):**
- **2-3 hours** to externalize config and test PyInstaller
- **Ready for Spain**: YES, if they only need to VIEW/APPROVE

### **For Full System (SMS Viewer + Conductor):**
- **Add 2-3 hours** for modem setup on Spain machine
- **Ready for Spain**: YES, but requires modem hardware

---

## **RECOMMENDED APPROACH:**

### **Phase 1: SMS Viewer Only (This Weekend)**
1. Externalize credentials (30 min)
2. Build executable (1 hour)
3. Test on your laptop (30 min)
4. Send to Spain, test remotely (1 hour)

**RESULT**: Spain can view, reply, approve, schedule campaigns

### **Phase 2: Add Conductor (Next Week)**
1. Ship USB modem to Spain
2. Install drivers remotely
3. Configure COM port
4. Test sending

**RESULT**: Spain can send SMS independently

---

## **SECURITY NOTES:**

⚠️ **IMPORTANT**: 
- `config.json` contains sensitive API keys
- Do NOT commit to public repos
- Share via encrypted channel (email, secure file transfer)
- Consider using environment variables for extra security

---

## **SUPPORT PLAN:**

### **For Spain Deployment:**
1. **Pre-deployment**: Test executable on 2nd machine
2. **During deployment**: Screen share with Spain team
3. **Post-deployment**: Create troubleshooting doc
4. **Ongoing**: Set up error logging to file

---

## **NEXT STEPS:**

1. **NOW**: Fix credentials (30 min) ← DO THIS FIRST
2. **TODAY**: Test PyInstaller build (1 hour)
3. **TODAY**: Test on 2nd machine (30 min)
4. **TOMORROW**: Ship to Spain (5 min)

---

**BOTTOM LINE**: You're ~3 hours away from being able to ship this to Spain for SMS viewing/approval. Full SMS sending requires modem hardware.

