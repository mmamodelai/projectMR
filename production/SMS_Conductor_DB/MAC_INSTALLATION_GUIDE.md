# 🍎 MAC INSTALLATION GUIDE - SMS Conductor UI

## **QUICK START FOR MAC USERS**

---

## **STEP 1: OPEN TERMINAL ON MAC**

### **Method 1: Spotlight Search (Easiest)**
1. Press `⌘ + Space` (Command + Space)
2. Type: `Terminal`
3. Press `Enter`
4. Terminal window opens!

### **Method 2: Finder**
1. Open **Finder**
2. Click **Applications** in sidebar
3. Open **Utilities** folder
4. Double-click **Terminal**

### **Method 3: Launchpad**
1. Press `F4` or swipe up with 4 fingers
2. Type: `Terminal`
3. Click Terminal icon

---

## **STEP 2: CHECK IF PYTHON IS INSTALLED**

In Terminal, type:

```bash
python3 --version
```

**Expected output:** `Python 3.8.x` or higher

### **If Python is NOT installed:**

**Option A: Install via Homebrew (Recommended)**
```bash
# Install Homebrew first (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Then install Python
brew install python3
```

**Option B: Download from Python.org**
1. Go to: https://www.python.org/downloads/
2. Download Python 3.8+ for macOS
3. Run installer
4. **IMPORTANT:** Check "Add Python to PATH" during installation

---

## **STEP 3: NAVIGATE TO PROJECT FOLDER**

In Terminal, navigate to where you extracted the SMS Conductor files:

```bash
# Example: If files are in Downloads
cd ~/Downloads/SMSConductorDB_v3

# Or if files are in Desktop
cd ~/Desktop/SMSConductorDB_v3

# Or if files are in Documents
cd ~/Documents/SMSConductorDB_v3
```

**💡 TIP:** You can drag the folder into Terminal to auto-fill the path!

---

## **STEP 4: INSTALL DEPENDENCIES**

### **Navigate to conductor-sms folder:**

```bash
cd conductor-sms
```

### **Install all dependencies:**

```bash
pip3 install -r requirements.txt
```

**Expected output:**
```
Collecting supabase>=2.0.0
Collecting python-dateutil>=2.8.0
Collecting pyserial>=3.5
Collecting python-dotenv>=1.0.0
...
Successfully installed supabase-2.x.x python-dateutil-2.x.x pyserial-3.x.x python-dotenv-1.x.x
```

### **If you get "pip3: command not found":**

Try:
```bash
python3 -m pip install -r requirements.txt
```

### **If you get permission errors:**

Add `--user` flag:
```bash
pip3 install --user -r requirements.txt
```

---

## **STEP 5: RUN THE APPLICATION**

### **Option 1: Run directly with Python**

```bash
python3 SMSconductor_DB.py
```

### **Option 2: Make it executable (one-time)**

```bash
chmod +x SMSconductor_DB.py
python3 SMSconductor_DB.py
```

### **Option 3: Create a launcher script**

Create a file called `START_SMS_VIEWER.sh`:

```bash
#!/bin/bash
cd "$(dirname "$0")"
python3 SMSconductor_DB.py
```

Make it executable:
```bash
chmod +x START_SMS_VIEWER.sh
```

Then double-click it in Finder, or run:
```bash
./START_SMS_VIEWER.sh
```

---

## **STEP 6: FIRST-TIME SQL SETUP**

⚠️ **BEFORE USING SCHEDULE BUTTONS:**

1. Open `CRITICAL_SQL_SETUP.md` in TextEdit
2. Follow the 2-minute SQL setup instructions
3. This enables the Schedule buttons

---

## **TROUBLESHOOTING**

### **"python3: command not found"**

**Solution:** Install Python (see Step 2)

### **"pip3: command not found"**

**Solution:** Use `python3 -m pip` instead:
```bash
python3 -m pip install -r requirements.txt
```

### **"Permission denied"**

**Solution:** Install to user directory:
```bash
pip3 install --user -r requirements.txt
```

### **"ModuleNotFoundError: No module named 'supabase'"**

**Solution:** Make sure you're in the `conductor-sms` folder:
```bash
cd conductor-sms
pip3 install -r requirements.txt
```

### **"SSL Certificate Error"**

**Solution:** Update certificates:
```bash
/Applications/Python\ 3.x/Install\ Certificates.command
```

Or install certifi:
```bash
pip3 install --upgrade certifi
```

### **"Tkinter not found"**

**Solution:** Install tkinter (usually included, but if missing):
```bash
# macOS usually has it, but if missing:
brew install python-tk
```

---

## **QUICK REFERENCE COMMANDS**

```bash
# Open Terminal
⌘ + Space → Type "Terminal" → Enter

# Check Python version
python3 --version

# Navigate to project
cd ~/Downloads/SMSConductorDB_v3/conductor-sms

# Install dependencies
pip3 install -r requirements.txt

# Run application
python3 SMSconductor_DB.py
```

---

## **CREATING A DESKTOP SHORTCUT (OPTIONAL)**

### **Create an AppleScript Launcher:**

1. Open **Script Editor** (Applications → Utilities)
2. Paste this:

```applescript
tell application "Terminal"
    do script "cd ~/Downloads/SMSConductorDB_v3/conductor-sms && python3 SMSconductor_DB.py"
    activate
end tell
```

3. Save as: `SMS Conductor.app`
4. Save to Desktop
5. Double-click to launch!

---

## **VERIFICATION CHECKLIST**

Before running, verify:

- [ ] Python 3.8+ installed (`python3 --version`)
- [ ] In correct folder (`cd conductor-sms`)
- [ ] Dependencies installed (`pip3 install -r requirements.txt`)
- [ ] No errors during installation
- [ ] SQL setup completed (see `CRITICAL_SQL_SETUP.md`)

---

## **FEATURES THAT WORK ON MAC**

✅ All tabs (All Messages, Reply, First Texts, Campaign Master, etc.)  
✅ Live Mode (15-second auto-refresh)  
✅ Smart double-click navigation  
✅ Flexible scheduling  
✅ Contact resolution (customers, budtenders, campaigns)  
✅ Mark as read  
✅ Always displays Pacific Time  

---

## **SYSTEM REQUIREMENTS**

- **macOS:** 10.14 (Mojave) or newer
- **Python:** 3.8 or higher
- **RAM:** 4GB minimum
- **Internet:** Required (connects to Supabase)

---

## **NEED HELP?**

**Common Issues:**
- Python not found → Install Python 3.8+
- Permission errors → Use `--user` flag
- Module errors → Make sure you're in `conductor-sms` folder
- SSL errors → Update certificates

**Contact:** Luis for support

---

## **NEXT STEPS AFTER INSTALLATION**

1. ✅ Run `python3 SMSconductor_DB.py`
2. ✅ Application window opens
3. ✅ Check "Live Mode (15s refresh)" to see auto-refresh timestamp
4. ✅ Complete SQL setup (see `CRITICAL_SQL_SETUP.md`)
5. ✅ Start managing campaigns!

---

**You're all set! 🚀**

