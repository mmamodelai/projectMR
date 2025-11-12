# SMS Conductor Database Viewer

**Version**: 3.0 (Master Queue System)  
**Platform**: Windows, macOS, Linux  
**Python**: 3.8+

## Features

✨ **Master Queue System** - Continuous message scheduling like a river/flow  
🎯 **Bullseye Scheduler** - Precise timing control (begins/middle/ends at)  
📝 **Popup Editor** - Edit messages in-place with character count  
🔄 **Column Sorting** - Click any header to sort (case-insensitive)  
🖱️ **Right-Click Workflows** - Approve, Schedule, Roll Back actions  
📊 **Selection Counter** - See how many messages you've selected  
📅 **Day-of-Week Display** - Know what day you're scheduling for  
🕐 **Scheduling Windows** - Auto-respects 9am-8pm business hours  
➕ **Add to Reply Messages** - NEW! Create follow-up conversations from sent messages  

## Quick Start

### Windows

**Option 1: Use EXE** (if provided)
1. Extract `SMSConductorDB.zip`
2. Run `SMSConductorDB.exe`

**Option 2: Run from Python**
```batch
pip install -r requirements.txt
python SMSconductor_DB.py
```

### macOS

**Option 1: Use Launcher** (Recommended)
```bash
# Make launcher executable (one time)
cd ~/Downloads/conductor-sms
chmod +x START_VIEWER_MAC.command

# Then double-click START_VIEWER_MAC.command
# OR run from terminal:
./run_mac.sh
```
First time: Installs dependencies (~30 seconds)  
After that: Launches instantly!

**Option 2: Manual Install**
```bash
# Install dependencies
pip3 install -r requirements.txt

# Run the app
python3 SMSconductor_DB.py
```

**See `README_MAC.md` for detailed Mac setup guide.**

### Linux

```bash
# Install Python and Tk
sudo apt install python3 python3-pip python3-tk

# Install dependencies
pip3 install -r requirements.txt

# Run the app
python3 SMSconductor_DB.py
```

## Configuration

### Setup Credentials

**1. Copy the template**
```bash
cp config.env.template .env
```

**2. Edit `.env` with your Supabase credentials**
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
CRM_URL=https://your-project.supabase.co
CRM_ANON_KEY=your_anon_key_here
```

**3. Run the app**
```bash
python SMSconductor_DB.py  # or python3 on Mac/Linux
```

## Master Queue System

### What is it?

The Master Queue System lets you schedule messages continuously, like a conveyor belt. No need to pick times for every message - just add them to the queue!

### Two Modes:

#### 📅 **Target Time Mode** (Classic Bullseye)
- Set specific date/time
- Choose positioning:
  - **Begins at** - First message at target time
  - **Middle** - Middle message at target time
  - **Ends at** - Last message at target time

#### ➕ **Add to Queue Mode** (NEW!)
- Finds last scheduled message automatically
- Continues from there with 5-7 min spacing
- Respects 9am-8pm scheduling windows
- **Perfect for continuous campaigns!**

### Example Workflow:

```
1. Sort by Dispensary → Select 10 messages
2. Right-click → "Schedule Selected..."
3. Choose: "Add to Current Queue"
4. Click "Schedule Messages" → Done!

Messages automatically append to end of queue:
  Last scheduled: 2:13 PM
  New messages:   2:19 PM, 2:25 PM, 2:31 PM... (5-7 min spacing)
```

## Features Guide

### Selection Counter
See "✓ 15 selected" next to stats - know how many messages you're working with

### Column Sorting
Click any column header to sort:
- Status, Name, Phone, Dispensary, Campaign, Time, Message
- Case-insensitive (firehouse = Firehouse = FIREHOUSE)
- Arrow indicators show sort direction (↕ → ↑ → ↓)

### Right-Click Actions
- **Suggested (SUG)**: Approve, Edit, Delete
- **Approved (APR)**: Schedule, Roll Back, Edit, Delete
- **Scheduled (SCH)**: Roll Back, Cancel, Edit

### Popup Editor
- Double-click any message to edit
- Real-time character count
- Shows dispensary in header
- Save changes directly to database

### Scheduling Windows
- Business hours: 9am - 8pm (PST)
- Before 9am → Jumps to 9am same day
- After 8pm → Jumps to 9am next day
- Automatically handles overnight scheduling!

## Documentation

- **Feature Guide**: `docs/SMS_VIEWER_ENHANCEMENTS.md`
- **Master Queue Details**: `docs/MASTER_QUEUE_SYSTEM.md`
- **Deployment Guide**: `README_DEPLOYMENT.md`

## Requirements

### Python Packages
```
supabase>=2.0.0
python-dateutil>=2.8.0
pyserial>=3.5
python-dotenv>=1.0.0
```

Install all:
```bash
pip install -r requirements.txt
```

### System Requirements
- **Windows**: Windows 10+
- **macOS**: macOS 10.15+
- **Linux**: Any modern distro with Python 3.8+ and Tk

## Troubleshooting

### "Supabase credentials not configured"
**Fix**: Create `.env` file with your credentials (see Configuration section)

### "No module named 'supabase'"
**Fix**: Run `pip install -r requirements.txt`

### Mac: "Python not found"
**Fix**: Use `python3` instead of `python`

### Windows: EXE doesn't start
**Fix**: Run from command prompt to see errors:
```batch
cd dist\SMSConductorDB
SMSConductorDB.exe
```

## Development

### Building EXE (Windows)
```batch
# Install PyInstaller
pip install pyinstaller

# Build
python conductor-sms\build_exe.py

# Output: dist\SMSConductorDB\SMSConductorDB.exe
```

### Building Mac App
```bash
# Install py2app
pip3 install py2app

# Build
python3 setup.py py2app

# Output: dist/SMSconductor_DB.app
```

## License

Proprietary - All Rights Reserved

## Support

For questions or issues, contact your administrator or check the documentation in the `docs/` folder.

---

**Version**: 3.0 (Master Queue System)  
**Last Updated**: November 10, 2025  
**Platform Support**: Windows, macOS, Linux
