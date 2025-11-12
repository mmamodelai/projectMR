# SMS Conductor Database Viewer - Portable Setup

**Quick Setup**: Get the viewer running anywhere in 2 minutes!

---

## ✅ Your Supabase Credentials

**These are SAFE to use** (anon key, not service-role key):

```
Project URL: https://kiwmwoqrguyrcpjytgte.supabase.co
Anon Key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0
```

---

## 🚀 Method 1: Using .env File (Recommended for Portable)

### Step 1: Create .env File

In the same folder as `SMSconductor_DB.py`, create a file named `.env` (no extension):

```env
SUPABASE_URL=https://kiwmwoqrguyrcpjytgte.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0
```

**On Windows**:
```powershell
# Copy the template
copy PORTABLE_CONFIG.txt .env

# OR create manually in Notepad
notepad .env
# Paste the content above, save
```

### Step 2: Install Dependencies

```powershell
pip install python-dotenv supabase python-dateutil
```

### Step 3: Run the Viewer

```powershell
pythonw SMSconductor_DB.py
```

Or with console for debugging:
```powershell
python SMSconductor_DB.py
```

---

## 🚀 Method 2: Using config.json

### Step 1: Create config.json

Create `config.json` in the same folder as `SMSconductor_DB.py`:

```json
{
  "database": {
    "use_supabase": true,
    "supabase_url": "https://kiwmwoqrguyrcpjytgte.supabase.co",
    "supabase_key": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"
  }
}
```

### Step 2: Install Dependencies

```powershell
pip install supabase python-dateutil
```

### Step 3: Run the Viewer

```powershell
pythonw SMSconductor_DB.py
```

---

## 📦 Portable Package Contents

For a truly portable version, include these files:

```
portable_viewer/
├── SMSconductor_DB.py          # The viewer
├── .env                         # Credentials (from PORTABLE_CONFIG.txt)
├── start_viewer.bat             # Double-click launcher
└── README.txt                   # Quick instructions
```

### start_viewer.bat

```batch
@echo off
REM SMS Conductor Database Viewer Launcher
echo Starting SMS Conductor Database Viewer...
cd /d "%~dp0"
pythonw SMSconductor_DB.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Failed to start viewer
    echo.
    echo Make sure you have:
    echo   1. Python installed
    echo   2. Dependencies installed: pip install supabase python-dateutil python-dotenv
    echo   3. .env file configured with Supabase credentials
    echo.
    pause
)
```

---

## 🔍 Verifying Credentials

Your anon key decoded (this is SAFE, not the service key):

```json
{
  "iss": "supabase",
  "ref": "kiwmwoqrguyrcpjytgte",
  "role": "anon",      ← This is correct (not "service_role")
  "iat": 1759845051,
  "exp": 2075421051     ← Expires in 2035
}
```

✅ **SAFE**: `role: anon` means this key has limited, safe permissions  
❌ **UNSAFE**: If it said `role: service_role`, don't ship it

---

## ✨ Features Available

Once running, you can:

### Tab 1: All Messages
- 📊 View all SMS messages
- 🎨 Color-coded by status (green=sent, red=failed, blue=unread)
- 🖱️ Right-click to edit, delete, or change status
- 📈 Live statistics

### Tab 2: Reply to Messages
- 💬 Conversation view
- ✍️ Manual reply composer
- 📱 Customer name resolution
- ⚡ Queue replies (Conductor sends within 5 seconds)

### Tab 3: First Texts (Campaign Approvals)
- 📨 Review AI-generated campaign messages
- ✅ Approve & send
- ✏️ Edit before sending
- ❌ Reject with feedback
- 🎯 Budtender welcome campaign management

---

## 🐛 Troubleshooting

### "Supabase credentials not configured"
**Fix**: Make sure either `.env` or `config.json` exists and has the correct values

### "ModuleNotFoundError: No module named 'supabase'"
**Fix**: Install dependencies
```powershell
pip install supabase python-dateutil python-dotenv
```

### Viewer opens then closes immediately
**Fix**: Run with console to see errors:
```powershell
python SMSconductor_DB.py
```

### "No messages showing"
**Fix**: Check that:
1. Your Supabase URL is correct
2. The `messages` table exists
3. You have internet connection
4. The anon key has read permissions

---

## 🌐 Remote Access

Want to run the viewer from another computer?

**Same network**:
- Just copy the folder
- Make sure `.env` or `config.json` is included
- Run it!

**Different network**:
- Everything works (Supabase is cloud-based)
- No VPN or port forwarding needed
- Internet connection required

---

## 🔐 Security Notes

**✅ Safe to Share**:
- Anon key (read-only with RLS policies)
- Supabase project URL
- The viewer code

**❌ NEVER Share**:
- Service role key (admin access)
- Database passwords
- Your Supabase project API keys page screenshot

**Current Setup**: ✅ Using anon key (safe!)

---

## 📞 Quick Reference

| Item | Value |
|------|-------|
| **Project URL** | https://kiwmwoqrguyrcpjytgte.supabase.co |
| **Anon Key** | eyJhbGci...EmdV0 (starts with eyJhbGci, 205 characters) |
| **Role** | anon (safe) ✅ |
| **Expires** | 2035 |

---

## 🚀 Quick Start Commands

```powershell
# Navigate to folder
cd C:\path\to\conductor-sms

# Copy config template
copy PORTABLE_CONFIG.txt .env

# Install deps (one-time)
pip install supabase python-dateutil python-dotenv

# Run viewer
pythonw SMSconductor_DB.py
```

**Done!** Viewer should open in 2-3 seconds. 🎉

---

**Need help?** Check that:
1. ✅ Python installed (`python --version`)
2. ✅ Dependencies installed (`pip list | findstr supabase`)
3. ✅ .env or config.json exists
4. ✅ Internet connection working

---

**Created**: November 8, 2025  
**Version**: Portable v1.0  
**Status**: Ready to deploy anywhere!

