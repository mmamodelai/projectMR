# SMS Conductor Database Viewer - Deployment Checklist
**Date**: November 10, 2025

## Two Versions to Deploy

### 1. Internal Version (With Credentials) - For Your Use
**Contains**: Hardcoded Supabase credentials  
**Format**: Windows EXE  
**Distribution**: Secure/private (not public!)

### 2. Customer Version (Clean) - For GitHub
**Contains**: No credentials (uses .env file)  
**Format**: Python source code  
**Distribution**: GitHub repository  
**Platforms**: Windows (Python), Mac (Python), Linux (Python)

---

## PART 1: Build Internal EXE (With Credentials)

### ✅ Checklist

- [ ] **Step 1**: Open PowerShell in `C:\Dev\conductor`

- [ ] **Step 2**: Run build script
```batch
.\BUILD_EXE.bat
```

- [ ] **Step 3**: Wait for build to complete (~2-5 minutes)

- [ ] **Step 4**: Test the EXE
```batch
cd dist\SMSConductorDB
.\SMSConductorDB.exe
```

- [ ] **Step 5**: Verify features work:
  - [ ] Opens successfully
  - [ ] Connects to database
  - [ ] Shows messages
  - [ ] Selection counter works
  - [ ] Right-click menus appear
  - [ ] Bullseye scheduler opens
  - [ ] Master Queue mode available

- [ ] **Step 6**: Zip the folder
```powershell
# In C:\Dev\conductor\dist
Compress-Archive -Path SMSConductorDB -DestinationPath SMSConductorDB_v3.0_Internal.zip
```

- [ ] **Step 7**: Store securely (this has your credentials!)

**Output**: `SMSConductorDB_v3.0_Internal.zip` (for your internal use)

---

## PART 2: Prepare GitHub Version (Clean)

### ✅ Checklist

- [ ] **Step 1**: Create a new folder for GitHub version
```powershell
cd C:\Dev
mkdir conductor-sms-github
cd conductor-sms-github
```

- [ ] **Step 2**: Copy clean files (NO credentials!)
```powershell
# Copy main files
copy C:\Dev\conductor\conductor-sms\SMSconductor_DB.py .
copy C:\Dev\conductor\conductor-sms\requirements.txt .
copy C:\Dev\conductor\conductor-sms\config.env.template .
copy C:\Dev\conductor\conductor-sms\README.md .
copy C:\Dev\conductor\conductor-sms\README_DEPLOYMENT.md .
copy C:\Dev\conductor\conductor-sms\.gitignore .

# Copy docs folder
xcopy C:\Dev\conductor\docs docs\ /E /I
```

- [ ] **Step 3**: Verify NO credentials in files
  - [ ] Open `SMSconductor_DB.py` - check NO hardcoded keys
  - [ ] Open `config.env.template` - check only placeholders
  - [ ] No `.env` file present
  - [ ] No `config.json` with real credentials

- [ ] **Step 4**: Test clean version with `.env` file
```powershell
# Create .env for testing
copy config.env.template .env
# Edit .env with your test credentials
notepad .env
# Test it works
python SMSconductor_DB.py
```

- [ ] **Step 5**: Remove test `.env` (IMPORTANT!)
```powershell
del .env
```

- [ ] **Step 6**: Create Git repository
```powershell
git init
git add .
git commit -m "Initial commit: SMS Conductor DB Viewer v3.0 (Master Queue System)"
```

- [ ] **Step 7**: Push to GitHub (Private Repository!)
```powershell
# Create private repo on GitHub first, then:
git remote add origin https://github.com/YOUR-USERNAME/sms-conductor-db.git
git branch -M main
git push -u origin main
```

**Output**: GitHub repository (private) with clean code

---

## PART 3: Customer Delivery

### For Customer Who Needs Both Windows and Mac:

#### Option A: Send GitHub Access + Credentials Separately

**Step 1**: Add customer as collaborator to private GitHub repo

**Step 2**: Send credentials SEPARATELY (secure email/encrypted)
```
SUPABASE_URL=https://...
SUPABASE_ANON_KEY=eyJ...
CRM_URL=https://...
CRM_ANON_KEY=eyJ...
```

**Step 3**: Send setup instructions:
```
Windows:
1. Download Python 3.11 from python.org
2. Clone repo: git clone https://github.com/YOUR-USERNAME/sms-conductor-db.git
3. Install: pip install -r requirements.txt
4. Create .env file with credentials I sent separately
5. Run: python SMSconductor_DB.py

Mac:
1. Open Terminal
2. Clone repo: git clone https://github.com/YOUR-USERNAME/sms-conductor-db.git
3. Install: pip3 install -r requirements.txt
4. Create .env file with credentials I sent separately
5. Run: python3 SMSconductor_DB.py
```

#### Option B: Send Pre-Configured Package (Less Secure)

**Windows**:
- Send them `SMSConductorDB_v3.0_Internal.zip` (EXE with credentials baked in)
- They just extract and run

**Mac**:
- Create a zip with Python files + `.env` already configured
- Send via secure channel
- They extract and run `python3 SMSconductor_DB.py`

---

## PART 4: Mac-Specific Setup (For Customer)

### Customer Instructions for Mac:

**1. Check Python Version**
```bash
python3 --version
# Should be 3.8 or higher
```

**2. If Python Not Installed**
```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.11
```

**3. Install Dependencies**
```bash
cd path/to/sms-conductor-db
pip3 install -r requirements.txt
```

**4. Configure Credentials**
```bash
# Copy template
cp config.env.template .env

# Edit with credentials
nano .env
# OR
open -e .env
```

**5. Run the App**
```bash
python3 SMSconductor_DB.py
```

**6. (Optional) Create Launcher**
```bash
cat > "Launch SMS Viewer.command" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
python3 SMSconductor_DB.py
EOF

chmod +x "Launch SMS Viewer.command"
```

Now they can double-click `Launch SMS Viewer.command` to start!

---

## Quick Reference

### Files for Internal Use (With Credentials):
```
✅ dist\SMSConductorDB\SMSConductorDB.exe  (Windows EXE)
✅ SMSConductorDB_v3.0_Internal.zip         (Zipped version)
```

### Files for GitHub (Clean):
```
✅ conductor-sms-github\                    (Clean repo folder)
   ├── SMSconductor_DB.py
   ├── requirements.txt
   ├── config.env.template                  (NO real credentials!)
   ├── README.md
   ├── README_DEPLOYMENT.md
   ├── .gitignore
   └── docs\
```

### What NOT to Put on GitHub:
```
❌ .env                                      (NEVER!)
❌ config.json                               (NEVER!)
❌ *_credentials.json                        (NEVER!)
❌ dist\SMSConductorDB\SMSConductorDB.exe   (Has credentials!)
```

---

## Testing Checklist

### Before Delivery:

**Internal EXE**:
- [ ] Runs on clean Windows 10 machine
- [ ] Connects to database automatically
- [ ] All features work

**GitHub Version**:
- [ ] Clone fresh copy
- [ ] NO credentials in any file
- [ ] Create `.env` with test credentials
- [ ] `pip install -r requirements.txt` works
- [ ] `python SMSconductor_DB.py` works
- [ ] Test on Mac (if possible)

---

## Support Documentation Included

**For Customer**:
- `README.md` - Quick start guide
- `README_DEPLOYMENT.md` - Detailed deployment guide
- `docs/SMS_VIEWER_ENHANCEMENTS.md` - Feature guide
- `docs/MASTER_QUEUE_SYSTEM.md` - Master Queue system details

**For You**:
- `WORKLOG.md` - Complete development history
- This checklist!

---

## Final Steps

- [ ] Build internal EXE
- [ ] Test internal EXE
- [ ] Zip internal EXE
- [ ] Store internal version securely

- [ ] Create clean GitHub folder
- [ ] Verify NO credentials
- [ ] Test clean version
- [ ] Push to GitHub (private repo)

- [ ] Send customer GitHub access
- [ ] Send credentials separately (secure channel)
- [ ] Send setup instructions

- [ ] Customer confirms Windows working
- [ ] Customer confirms Mac working

✅ **DEPLOYMENT COMPLETE!**

---

**Last Updated**: November 10, 2025  
**Version**: 3.0 (Master Queue System)

