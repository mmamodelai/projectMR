# SMS Conductor Database Viewer - Mac Installation

## Quick Start (Mac Users)

### 1. Download
Download the `conductor-sms` folder to your Mac.

### 2. Make Launcher Executable
Open Terminal and navigate to the folder:
```bash
cd ~/Downloads/conductor-sms
chmod +x run_mac.sh
```

### 3. Run
Double-click `run_mac.sh` or run from Terminal:
```bash
./run_mac.sh
```

The launcher will automatically:
- ✅ Check for Python 3
- ✅ Create a virtual environment
- ✅ Install all dependencies
- ✅ Launch the viewer

---

## First Time Setup (One-Time Only)

The first time you run `run_mac.sh`, it will:
1. Create a `venv` folder (virtual environment)
2. Download and install dependencies
3. Launch the viewer

**This takes about 30 seconds.** After that, it launches instantly!

---

## Manual Installation (If Automatic Fails)

If `run_mac.sh` doesn't work, install manually:

### Step 1: Install Python 3
Mac comes with Python 2. Install Python 3:
```bash
brew install python3
```
Or download from: https://www.python.org/downloads/

### Step 2: Create Virtual Environment
```bash
cd ~/Downloads/conductor-sms
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run Viewer
```bash
pythonw SMSconductor_DB.py
```
Or:
```bash
python3 SMSconductor_DB.py
```

---

## Credentials

**This version has credentials embedded** for your convenience.

If you need to change credentials later:
1. Create a `.env` file in the `conductor-sms` folder
2. Copy from `config.env.template`
3. Update with your credentials

---

## Troubleshooting

### "Permission Denied" Error
Make the script executable:
```bash
chmod +x run_mac.sh
```

### "Python 3 Not Found"
Install Python 3:
```bash
brew install python3
```

### "Module Not Found" Errors
Reinstall dependencies:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### GUI Doesn't Open
Try using `pythonw` instead of `python3`:
```bash
pythonw SMSconductor_DB.py
```

---

## Uninstall

Delete the folder:
```bash
rm -rf ~/Downloads/conductor-sms
```

That's it! No system-wide installation, completely portable.

---

## Features

✅ All Messages View  
✅ Reply to Messages  
✅ Campaign Master  
✅ Bullseye Scheduler  
✅ Message Editing  
✅ Right-Click Workflows  
✅ Auto-Refresh  
✅ **NEW: Add to Reply Messages** - Create follow-up conversations from sent messages

---

## Support

For issues or questions, contact your system administrator.

Version: 1.0 (2025-11-10)  
Platform: macOS 10.14+  
Python: 3.8+

