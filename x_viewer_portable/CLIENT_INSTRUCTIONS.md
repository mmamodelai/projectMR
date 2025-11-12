# Dispensary & Budtender Viewer - Client Package

## What This Is
A portable database viewer for your dispensary and budtender data. This connects to a cloud database and displays all your budtender information in an easy-to-use interface.

## What You Get
- **524 budtenders** from **112 dispensaries**
- **Live search** - find budtenders instantly as you type
- **Points system** - view and edit budtender points
- **Professional interface** - clean, modern design

## Requirements
- **Windows, Mac, or Linux** computer
- **Python 3.7 or higher** (free from python.org)
- **Internet connection** (connects to cloud database)

## How to Install & Run

### Option 1: Automatic Setup (Recommended)
1. **Double-click**: `start_dispensary_viewer_portable.bat`
2. **Wait**: It will install required packages automatically
3. **Done**: Viewer opens automatically

### Option 2: Manual Setup
1. **Install Python**: Download from python.org
2. **Open Command Prompt/Terminal**
3. **Run**: `pip install supabase`
4. **Run**: `python dispensary_viewer_portable.py`

## Features

### 🔍 Live Search
- Type "james" → instantly shows all budtenders with "james" in their name
- Type "phenos" → shows all budtenders from Phenos dispensary
- **Real-time filtering** as you type

### 📊 Dispensary List
- **Sorted by budtender count** (largest first)
- Phenos (52 budtenders) at the top
- Click any dispensary to see its budtenders

### 👥 Budtender Details
- **Dispensary | Name | Email | Phone | Points**
- **Right-click** any budtender to edit their points
- **Sortable** by points (highest first)

### 🎯 Points System
- **View points** for each budtender
- **Edit points** by right-clicking
- **Filter** by minimum points

## Troubleshooting

### "Python not found"
- Install Python from python.org
- Make sure to check "Add Python to PATH" during installation

### "supabase package not found"
- Run: `pip install supabase`
- Or use the automatic batch file

### "Failed to connect to Supabase"
- Check your internet connection
- The database is hosted in the cloud

### Viewer won't start
- Make sure Python 3.7+ is installed
- Try running: `python --version`
- Should show Python 3.7 or higher

## Data Security
- **Read-only access** by default
- **Points editing** requires right-click
- **Cloud database** - always up-to-date
- **No local data storage** - always fresh

## Support
If you have issues:
1. Try the automatic batch file first
2. Check your internet connection
3. Make sure Python is installed correctly
4. Contact support if problems persist

---
**Ready to use!** Just double-click the batch file and start viewing your budtender data.
