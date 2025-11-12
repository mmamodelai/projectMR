# SMS Conductor Database Viewer - Deployment Guide
**Version**: 3.0 (Master Queue System)  
**Date**: November 10, 2025

## Overview

This guide covers deploying the SMS Conductor Database Viewer for:
- **Windows** (EXE file)
- **Mac** (Python script)
- **Linux** (Python script)

## Features

✅ Master Queue System (continuous message scheduling)  
✅ Bullseye Scheduler (precise timing control)  
✅ Column Sorting (case-insensitive)  
✅ Right-Click Workflow Actions  
✅ Popup Message Editor  
✅ Selection Counter  
✅ Day-of-Week Display  

---

## Windows Deployment (EXE)

### Option 1: Use Pre-Built EXE (Easiest)

**Download**: Get `SMSConductorDB.zip` from releases

**Installation**:
1. Extract `SMSConductorDB.zip`
2. Run `SMSConductorDB.exe`
3. Done! (credentials are built-in)

### Option 2: Build Your Own EXE

**Requirements**:
- Python 3.8+ installed
- PyInstaller

**Steps**:
```batch
# 1. Install PyInstaller
pip install pyinstaller

# 2. Run build script
cd conductor-sms
python build_exe.py

# 3. Find EXE in dist\SMSConductorDB\
```

**Build Output**:
```
dist\
  └── SMSConductorDB\
      ├── SMSConductorDB.exe  ← Main executable
      ├── _internal\           ← Dependencies
      └── docs\                ← Documentation
```

**Distribution**:
1. Zip the entire `SMSConductorDB` folder
2. Share the zip file
3. Recipients extract and run `SMSConductorDB.exe`

---

## Mac Deployment (Python)

### Requirements

- Python 3.8+ (comes with most Macs)
- pip (Python package manager)

### Installation Steps

**1. Install Python (if needed)**
```bash
# Check if Python is installed
python3 --version

# If not installed, install via Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python@3.11
```

**2. Install Dependencies**
```bash
cd conductor-sms
pip3 install -r requirements.txt
```

**3. Configure Credentials**
```bash
# Copy template
cp config.env.template .env

# Edit with your credentials
nano .env
# OR
open -e .env
```

**Example `.env` file**:
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1...
CRM_URL=https://your-project.supabase.co
CRM_ANON_KEY=eyJhbGciOiJIUzI1...
```

**4. Run the App**
```bash
python3 SMSconductor_DB.py
```

### Create Mac Launcher (Optional)

**Create a .command file** for easy launching:

```bash
# Create launcher
cat > "Launch SMS Viewer.command" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
python3 SMSconductor_DB.py
EOF

# Make executable
chmod +x "Launch SMS Viewer.command"
```

Now double-click `Launch SMS Viewer.command` to start!

---

## Linux Deployment

### Ubuntu/Debian
```bash
sudo apt update
sudo apt install python3 python3-pip python3-tk
pip3 install -r requirements.txt
python3 SMSconductor_DB.py
```

### Fedora/RHEL
```bash
sudo dnf install python3 python3-pip python3-tkinter
pip3 install -r requirements.txt
python3 SMSconductor_DB.py
```

---

## Configuration Options

### Environment Variables

The app reads credentials from:
1. Environment variables (`.env` file)
2. `config.json` (fallback)

**Priority**: `.env` > `config.json`

### Config File (`config.json`)

Alternative to `.env`:
```json
{
  "database": {
    "supabase_url": "https://your-project.supabase.co",
    "supabase_key": "your_key_here"
  }
}
```

---

## Troubleshooting

### Windows

**Issue**: "Windows protected your PC" warning  
**Fix**: Click "More info" → "Run anyway" (unsigned executable)

**Issue**: EXE doesn't start  
**Fix**: Run from command prompt to see error:
```batch
cd dist\SMSConductorDB
SMSConductorDB.exe
```

### Mac

**Issue**: "Python not found"  
**Fix**: Use `python3` instead of `python`

**Issue**: "tkinter not found"  
**Fix**: 
```bash
brew install python-tk@3.11
```

**Issue**: Permission denied  
**Fix**:
```bash
chmod +x SMSconductor_DB.py
```

### Common Issues

**Issue**: "Supabase credentials not configured"  
**Fix**: Create `.env` file with your credentials

**Issue**: "No module named 'supabase'"  
**Fix**: Install dependencies:
```bash
pip install -r requirements.txt
```

**Issue**: Database connection fails  
**Fix**: Check your Supabase URL and key in `.env`

---

## GitHub Packaging (Clean Version)

### For Customers (No Credentials)

**Files to Include**:
```
conductor-sms/
├── SMSconductor_DB.py           # Main script
├── requirements.txt             # Dependencies
├── config.env.template          # Config template
├── README_DEPLOYMENT.md         # This file
├── docs/
│   ├── SMS_VIEWER_ENHANCEMENTS.md
│   └── MASTER_QUEUE_SYSTEM.md
└── .gitignore                   # Ignore .env
```

**Files to EXCLUDE** (add to `.gitignore`):
```
.env
config.json
*.pyc
__pycache__/
*.log
dist/
build/
*.spec
```

### Create .gitignore

```bash
# Credentials (NEVER commit!)
.env
config.json
*_credentials.json

# Python
*.pyc
__pycache__/
*.pyo
*.pyd
.Python

# Build artifacts
build/
dist/
*.spec
*.exe

# Logs
*.log
logs/

# OS files
.DS_Store
Thumbs.db
```

---

## Distribution Checklist

### Internal Distribution (With Credentials)
- [ ] Build EXE with credentials baked in
- [ ] Test EXE on clean Windows machine
- [ ] Zip `SMSConductorDB` folder
- [ ] Share via secure method (not public!)

### Customer Distribution (Clean)
- [ ] Remove all credentials from code
- [ ] Create `config.env.template`
- [ ] Test with `.env` file configuration
- [ ] Write setup instructions
- [ ] Push to GitHub (private repo)
- [ ] Send customer repo access + credentials separately

---

## Advanced: Creating Mac App Bundle

For a more native Mac experience:

**1. Install py2app**
```bash
pip3 install py2app
```

**2. Create setup.py**
```python
from setuptools import setup

APP = ['SMSconductor_DB.py']
DATA_FILES = ['docs']
OPTIONS = {
    'argv_emulation': True,
    'packages': ['supabase', 'tkinter'],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
```

**3. Build**
```bash
python3 setup.py py2app
```

**Output**: `dist/SMSconductor_DB.app`

---

## Support

**Documentation**:
- `docs/SMS_VIEWER_ENHANCEMENTS.md` - Feature guide
- `docs/MASTER_QUEUE_SYSTEM.md` - Queue system details
- `WORKLOG.md` - Development history

**Questions?** Check the docs first, then contact support.

---

**Last Updated**: November 10, 2025  
**Version**: 3.0  
**Platform Support**: Windows 10+, macOS 10.15+, Linux

