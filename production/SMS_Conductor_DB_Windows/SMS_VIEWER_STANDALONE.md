# SMS Viewer - Standalone Git Repository

## **CREATE SEPARATE REPO**

---

### **Files to Include:**

```
sms-viewer-beta/
├── SMSconductor_DB.py          # Main application
├── requirements.txt            # Python dependencies
├── START_SMS_VIEWER.bat        # Windows launcher
├── README.md                   # User documentation
├── SETUP.md                    # Installation guide
├── CRITICAL_SQL_SETUP.md       # SQL function deployment
├── .gitignore                  # Don't commit logs, cache
└── LICENSE                     # Your license choice
```

---

### **Commands to Create Repo:**

```bash
# Create new directory
mkdir sms-viewer-beta
cd sms-viewer-beta

# Copy files
cp ../conductor-sms/SMSconductor_DB.py .
cp ../conductor-sms/requirements.txt .
cp ../conductor-sms/START_SMS_VIEWER.bat .
cp ../conductor-sms/CRITICAL_SQL_SETUP.md .

# Initialize Git
git init
git add .
git commit -m "Initial commit - SMS Viewer Beta v1.0"

# Create GitHub repo (via web or CLI)
gh repo create sms-viewer-beta --public --source=. --push
```

---

### **README.md (for new repo):**

```markdown
# SMS Conductor - Beta Release v1.0

Professional SMS campaign management system with live updates and smart scheduling.

## Features

✅ View all messages in real-time  
✅ Reply to customers manually  
✅ Approve AI-generated campaigns  
✅ Schedule campaigns (flexible batch sizes)  
✅ Campaign pipeline visibility (SUG → APR → SCH → sent)  
✅ Mark conversations as read  
✅ Live Mode (15-second auto-refresh)  
✅ Smart double-click navigation  
✅ Color-coded status indicators  
✅ **Always displays Pacific Standard Time** (regardless of location)  

## Quick Start

### Requirements
- Python 3.8 or higher
- Internet connection (connects to Supabase)
- Windows/Mac/Linux

### Installation

1. **Install Python 3.8+**
   - Download from https://python.org
   - Check "Add Python to PATH" during installation

2. **Install Dependencies**
   ```bash
   pip install supabase python-dateutil
   ```

3. **Run Application**
   ```bash
   # Windows:
   START_SMS_VIEWER.bat
   
   # Or double-click:
   SMSconductor_DB.py
   
   # Or command line:
   pythonw SMSconductor_DB.py
   ```

### First-Time Setup

⚠️ **CRITICAL**: Before using Schedule buttons, you must deploy SQL functions to Supabase.

See: `CRITICAL_SQL_SETUP.md`

## Usage

### Tabs

1. **All Messages** - Raw message history
2. **Reply to Messages** - Unread inbox (right-click to mark read)
3. **First Texts** - Approve first contact messages
4. **Campaign Master** - Complete pipeline view (all statuses)
5. **Approved** - Messages ready to schedule
6. **Scheduled** - Timeline of upcoming sends

### Key Features

**Live Mode**: Check the checkbox (top-right) for 15-second auto-refresh

**Smart Double-Click**: 
- If contact has conversation history → Opens Reply tab
- If first contact (no history) → Opens First Texts tab

**Flexible Scheduling**:
- Type any number (e.g., `10`) + click "Schedule"
- Or click "Schedule ALL" to queue everything

**Mark as Read**:
- Right-click any conversation → "Mark as Read"
- Removes from Reply tab inbox

**Color-Coded Status**:
- 🟡 Yellow = SUG (needs approval)
- 🔵 Blue = APR (ready to schedule)
- 🟢 Light Green = SCH (scheduled)
- 🟢 Green = sent (delivered)

### Time Zones

⏰ **All times display in Pacific Standard Time (PST)** regardless of your location.

This ensures consistency across teams in different time zones.

## Architecture

```
SMS Viewer (Spain, anywhere)
       ↓
Supabase Database (Cloud)
       ↑
Conductor (California)
       ↓
USB Modem → SMS Sent
```

**Benefits**:
- No modem needed for SMS Viewer users
- Real-time sync across all users
- Centralized SMS sending (Conductor)
- Scalable (add unlimited viewers)

## Troubleshooting

### "Could not find the function public.schedule_approved_messages"
- See `CRITICAL_SQL_SETUP.md`
- Must deploy SQL functions to Supabase (one-time setup)

### "Failed to open: 'SMSViewer' object has no attribute..."
- Update to latest version (v1.0+)
- This was fixed in recent release

### Messages not sending
- Normal! SMS Viewer approves/schedules only
- Conductor (separate system) sends messages
- Contact administrator if urgent

### Database not loading
- Check internet connection
- Verify Supabase isn't down
- Click Refresh button
- Enable Live Mode

## Support

**Version**: Beta Release v1.0  
**License**: Proprietary (custom software for client)  
**Support**: Contact Luis for issues/feedback

## Changelog

### v1.0 (2025-11-08)
- Initial beta release
- All core features implemented
- Live Mode with 15-second refresh
- Flexible scheduling (N messages or ALL)
- Smart double-click navigation
- Mark as read functionality
- Always displays PST time
- Beta release branding

## Development

**Tech Stack**:
- Python 3.8+
- Tkinter (GUI)
- Supabase (Database)
- PostgreSQL (via Supabase)

**Dependencies**:
- `supabase` - Database client
- `python-dateutil` - Timezone handling

## Future Enhancements (v1.1+)

- Config file for credentials
- Built-in update checker
- Export campaign reports
- Custom scheduling rules per dispensary
- Dark mode
- Multi-language support

---

**Built with ❤️ for professional SMS campaign management**
```

---

### **.gitignore:**

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Config (if you externalize credentials later)
config.json
config.local.json

# Database
*.db
*.db-journal

# Temporary
*.tmp
*.bak
```

---

### **Why Separate Repo?**

✅ **Clean distribution** - Only SMS Viewer files  
✅ **Independent versioning** - Separate from Conductor  
✅ **Easier deployment** - Clone and run  
✅ **Open source potential** - Could make public later  
✅ **CI/CD ready** - GitHub Actions for releases  

---

### **Next Steps:**

1. Create `sms-viewer-beta` folder
2. Copy files listed above
3. Create README.md with content above
4. Initialize Git repo
5. Push to GitHub
6. Share repo link with Spain

**Deployment becomes:** "Clone this repo, run pip install, done!"


