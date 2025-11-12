# Conductor System Architecture - Complete Guide

## Executive Summary

The **Conductor System** is a polling-based SMS management solution that solves the fundamental problem of COM port conflicts when handling bidirectional SMS communication. Unlike continuous listening approaches, it uses brief connect/disconnect cycles to ensure the modem is never locked.

**Status**: Production-ready, 95 messages processed successfully
**Location**: `C:\Dev\n8n budtenders\Olive\`

---

## 🎯 Core Problem Statement

### The Challenge
USB modems (SIM7600G-H) have a critical limitation: **only ONE process can access the COM port at a time**. This creates a conflict:
- **Continuous listening** = COM port locked → cannot send messages
- **Continuous sending** = COM port locked → cannot receive messages

### The Solution: Polling Architecture
The Conductor System uses a **connect → poll → disconnect → repeat** pattern:
1. Connect to modem (2-3 seconds)
2. Check for incoming messages
3. Disconnect from modem
4. Check database for queued outgoing messages
5. Reconnect to send (if needed)
6. Disconnect
7. Wait 10 seconds
8. Repeat

**Result**: Bidirectional SMS without COM port conflicts.

---

## 📁 System Architecture

### Directory Structure
```
C:\Dev\n8n budtenders\Olive\
├── conductor_system.py          # Main system (polls modem every 10s)
├── database\
│   └── olive_sms.db             # SQLite database (95 messages)
├── logs\
│   └── conductor_system.log     # System logs
├── db_viewer.py                 # Real-time database viewer
├── start_conductor.bat          # Start conductor system
├── test_conductor.bat           # Send test messages
├── conductor_status.bat         # Check system status
└── start_db_viewer.bat          # Launch database viewer
```

---

## 🗄️ Database Schema

### `olive_sms.db` Structure

```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone_number TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TEXT NOT NULL,        -- 'unread', 'read', 'queued', 'sent', 'failed'
    direction TEXT NOT NULL,      -- 'inbound' or 'outbound'
    modem_index TEXT              -- Message index on modem (if applicable)
);

CREATE TABLE contacts (
    phone_number TEXT PRIMARY KEY,
    name TEXT,
    last_message_time DATETIME,
    message_count INTEGER DEFAULT 0
);
```

### Status Flow
- **Incoming Messages**: `unread` → `read`
- **Outgoing Messages**: `queued` → `sent` or `failed`

---

## 🔄 Message Flow Diagrams

### Incoming Message Flow
```
┌──────────────┐
│ SMS Arrives  │
│  at Modem    │
└──────┬───────┘
       │
       ▼
┌──────────────────────┐
│ Conductor Polls      │
│ Every 10 Seconds     │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ AT+CMGL="UNREAD"     │
│ Read Messages        │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Save to Database     │
│ status='unread'      │
│ direction='inbound'  │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Delete from Modem    │
│ Free up space        │
└──────────────────────┘
```

### Outgoing Message Flow
```
┌──────────────────────┐
│ External System      │
│ (n8n, API, Script)   │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Insert to Database   │
│ status='queued'      │
│ direction='outbound' │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Conductor Detects    │
│ Queued Message       │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Connect to Modem     │
│ Send via AT+CMGS     │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Update Status        │
│ 'sent' or 'failed'   │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Disconnect Modem     │
└──────────────────────┘
```

---

## 🔧 Core Components

### 1. `conductor_system.py`

**Purpose**: Main orchestrator that polls the modem and manages message flow.

**Key Methods**:
```python
class ConductorSystem:
    def __init__(self, port="COM24", db_path="database/olive_sms.db", poll_interval=10)
    
    def run(self):
        """Main polling loop - runs continuously"""
        
    def _poll_for_incoming(self):
        """Connect to modem, check for new messages, disconnect"""
        
    def _process_outgoing_queue(self):
        """Check DB for queued messages, send them"""
        
    def _send_sms(self, phone_number, message):
        """Send SMS via modem using AT+CMGS"""
        
    def _save_incoming_message(self, phone_number, content):
        """Save received message to database"""
```

**Polling Cycle**:
1. Connect to `COM24` (SIM7600G-H modem)
2. Send `AT+CMGL="UNREAD"` (get unread messages)
3. Parse response and save to database
4. Send `AT+CMGD` (delete from modem)
5. Disconnect
6. Query database for `status='queued'`
7. If messages found: reconnect → send → disconnect
8. Sleep 10 seconds
9. Repeat

**Configuration**:
- `port`: COM port (default: COM24)
- `db_path`: SQLite database path (default: database/olive_sms.db)
- `poll_interval`: Seconds between polls (default: 10)

---

### 2. `db_viewer.py`

**Purpose**: Real-time terminal UI for viewing database contents.

**Features**:
- Auto-refreshes every 2 seconds
- Color-coded message status
- Statistics dashboard
- Message history
- Conversation view

**Usage**:
```bash
python db_viewer.py
```

**Keyboard Controls**:
- `r`: Refresh view
- `q`: Quit
- Auto-refresh: Every 2 seconds

---

## 🚀 How to Deploy from Scratch

### Prerequisites
1. **Hardware**:
   - SIM7600G-H USB modem
   - Active SIM card with SMS service
   - Windows PC with USB port

2. **Software**:
   - Python 3.8+
   - pip package manager
   - COM port drivers (usually auto-install)

3. **Python Packages**:
   ```bash
   pip install pyserial
   ```

### Step-by-Step Setup

#### 1. Identify COM Port
```bash
# PowerShell
python -c "import serial.tools.list_ports; print([p.device for p in serial.tools.list_ports.comports()])"
```
Example output: `['COM24', 'COM1']` → Your modem is likely `COM24`

#### 2. Create Directory Structure
```bash
New-Item -ItemType Directory -Path "Olive" -Force
New-Item -ItemType Directory -Path "Olive\database" -Force
New-Item -ItemType Directory -Path "Olive\logs" -Force
```

#### 3. Create Database
```python
# create_database.py
import sqlite3
import os

os.makedirs("database", exist_ok=True)
conn = sqlite3.connect("database/olive_sms.db")

conn.execute("""
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone_number TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TEXT NOT NULL,
    direction TEXT NOT NULL,
    modem_index TEXT
)
""")

conn.execute("""
CREATE TABLE IF NOT EXISTS contacts (
    phone_number TEXT PRIMARY KEY,
    name TEXT,
    last_message_time DATETIME,
    message_count INTEGER DEFAULT 0
)
""")

conn.commit()
conn.close()
print("Database created successfully!")
```

#### 4. Copy `conductor_system.py`
*(Full source code located at `C:\Dev\n8n budtenders\Olive\conductor_system.py`)*

Key configuration:
```python
# At top of conductor_system.py
PORT = "COM24"              # Your modem's COM port
DB_PATH = "database/olive_sms.db"
POLL_INTERVAL = 10          # Seconds between polls
```

#### 5. Create Batch Files

**`start_conductor.bat`**:
```batch
@echo off
echo Starting Conductor SMS System...
cd /d "%~dp0"
python conductor_system.py
pause
```

**`test_conductor.bat`**:
```batch
@echo off
if "%~2"=="" (
    echo Usage: test_conductor.bat ^<phone_number^> ^<message^>
    echo Example: test_conductor.bat +16199773020 "Test message"
    pause
    exit /b 1
)
python conductor_system.py test %1 %2
pause
```

**`conductor_status.bat`**:
```batch
@echo off
python conductor_system.py status
pause
```

**`start_db_viewer.bat`**:
```batch
@echo off
echo Starting Database Viewer...
python db_viewer.py
pause
```

#### 6. Test the System

**Test 1: Start Conductor**
```bash
.\start_conductor.bat
```
Expected output:
```
Starting Conductor SMS System...
2025-09-30 22:51:00,000 - Conductor - INFO - Conductor System started
2025-09-30 22:51:00,001 - Conductor - INFO - Polling every 10 seconds
2025-09-30 22:51:00,002 - Conductor - INFO - Checking for incoming messages...
```

**Test 2: Send Test Message**
```bash
.\test_conductor.bat +16199773020 "Test message from conductor"
```
Expected output:
```
Message queued successfully!
ID: 1
Phone: +16199773020
Message: Test message from conductor
```

**Test 3: View Database**
```bash
.\start_db_viewer.bat
```
You should see your test message with `status='queued'`, then `status='sent'` after 10 seconds.

**Test 4: Receive Message**
Send an SMS to your modem's phone number from another phone. Within 10 seconds, it should appear in the database viewer with `status='unread'`.

---

## 🔌 AT Command Reference

### Commands Used by Conductor

| Command | Purpose | Example |
|---------|---------|---------|
| `AT` | Test connection | `AT\r\n` → `OK` |
| `AT+CMGF=1` | Set text mode | `AT+CMGF=1\r\n` → `OK` |
| `AT+CNMI=2,1,0,0,0` | Disable auto-notifications | Sets up proper message storage |
| `AT+CMGL="UNREAD"` | List unread messages | Returns `+CMGL: 1,"REC UNREAD","+1234567890"...` |
| `AT+CMGL="ALL"` | List all messages | Returns all messages on SIM |
| `AT+CMGR=<index>` | Read message at index | `AT+CMGR=1\r\n` |
| `AT+CMGS="<number>"` | Send SMS | `AT+CMGS="+1234567890"\r\nHello\x1A` |
| `AT+CMGD=<index>` | Delete message | `AT+CMGD=1\r\n` |
| `AT+CPMS="SM"` | Set storage to SIM | Switches to SIM card storage |
| `AT+CPMS="ME"` | Set storage to phone | Switches to phone memory |

### Message Response Format
```
+CMGL: 1,"REC UNREAD","+16199773020","","25/09/30,22:45:10-28"
Testing at 1045
OK
```

Parsing:
- Index: `1`
- Status: `"REC UNREAD"`
- Phone: `"+16199773020"`
- Timestamp: `"25/09/30,22:45:10-28"` (YY/MM/DD,HH:MM:SS±TZ)
- Content: `"Testing at 1045"` (next line)

---

## 🔍 How the Conductor Avoids COM Port Conflicts

### Problem Scenario
```
┌─────────────┐
│  Receiver   │ ← Locks COM24 continuously
└─────────────┘
       ↓
   COM24 Busy!
       ↓
┌─────────────┐
│   Sender    │ ← Cannot access COM24
└─────────────┘
```

### Conductor Solution
```
Time: 0s    Connect → Poll → Disconnect
Time: 3s    Check DB for queued messages
Time: 4s    Connect → Send → Disconnect
Time: 7s    Sleep
Time: 17s   Connect → Poll → Disconnect
...
```

**Key Principle**: Modem is never held for more than 2-3 seconds. Any process can access it between conductor cycles.

---

## 📊 Performance Characteristics

### Timing
- **Incoming message detection**: ~10 seconds max (poll interval)
- **Outgoing message send**: ~10 seconds max (poll interval)
- **Modem access time**: 2-3 seconds per cycle
- **COM port availability**: ~7 seconds per 10-second cycle (70% uptime)

### Capacity
- **Messages per hour**: ~360 (1 per 10 seconds, realistically ~100-200)
- **SIM card limit**: 23 messages (automatically managed)
- **Database limit**: Unlimited (SQLite)
- **Concurrent processes**: Multiple (due to polling architecture)

---

## 🧪 Testing & Validation

### Test Checklist

#### ✅ Basic Functionality
- [ ] Conductor starts without errors
- [ ] Database connection established
- [ ] COM port accessible
- [ ] Modem responds to AT commands

#### ✅ Incoming Messages
- [ ] Send SMS to modem's number
- [ ] Message appears in database within 10 seconds
- [ ] Status is `unread`
- [ ] Direction is `inbound`
- [ ] Message deleted from modem

#### ✅ Outgoing Messages
- [ ] Queue message via `test_conductor.bat`
- [ ] Status is `queued`
- [ ] Message sends within 10 seconds
- [ ] Status updates to `sent`
- [ ] Message received on target phone

#### ✅ Database Viewer
- [ ] Viewer displays messages
- [ ] Auto-refresh works
- [ ] Statistics are accurate
- [ ] Colors display correctly

---

## 🛠️ Troubleshooting Guide

### Issue: "Could not open port 'COM24'"

**Cause**: Another process is using the COM port.

**Solution**:
```bash
# Check for Python processes
Get-Process python

# Kill all Python processes
taskkill /F /IM python.exe

# Or find specific process
Get-CimInstance Win32_PnPEntity | Where-Object { $_.Name -like "*COM24*" }
```

### Issue: "No messages being detected"

**Checks**:
1. Is conductor running? (`Get-Process python`)
2. Is modem connected? (Check Device Manager)
3. Is SIM card inserted and registered?
4. Are messages stored on SIM? (Check modem directly)

**Diagnosis**:
```bash
# Test modem connection
python -c "import serial; s=serial.Serial('COM24', 115200, timeout=5); s.write(b'AT\r\n'); print(s.read(100))"

# Expected: b'AT\r\nOK\r\n'
```

### Issue: "Messages not sending"

**Checks**:
1. Is message in database with `status='queued'`?
2. Is conductor running?
3. Is phone number in E.164 format? (e.g., `+16199773020`)
4. Is SMS service active on SIM?

**Manual Test**:
```python
import serial
ser = serial.Serial('COM24', 115200, timeout=5)
ser.write(b'AT+CMGF=1\r\n')
print(ser.read(100))
ser.write(b'AT+CMGS="+16199773020"\r\n')
print(ser.read(100))
ser.write(b'Test message\x1A')
print(ser.read(100))
ser.close()
```

### Issue: "Database locked"

**Cause**: Multiple processes accessing database simultaneously.

**Solution**:
- SQLite has built-in retry logic
- If persistent, check for zombie processes
- Consider adding `timeout` parameter to database connections

---

## 🔗 Integration Points

### n8n Workflow Integration

**Approach 1: Direct Database Access**
```javascript
// n8n SQLite node
const db = $input.all();
const result = db.query('SELECT * FROM messages WHERE status = "unread"');
return result;
```

**Approach 2: REST API** (if implemented)
```javascript
// n8n HTTP Request node
const response = await $http.post('http://localhost:5001/send-sms', {
    phone_number: '+16199773020',
    message: 'Hello from n8n'
});
```

**Approach 3: Python Script Node**
```python
# n8n Python node
import sqlite3
conn = sqlite3.connect('C:/Dev/n8n budtenders/Olive/database/olive_sms.db')
cursor = conn.execute("INSERT INTO messages (phone_number, content, status, direction) VALUES (?, ?, 'queued', 'outbound')", 
                      (phone_number, message))
conn.commit()
conn.close()
```

### GitHub Sync

**Manual Sync**:
```bash
cd "C:\Dev\n8n budtenders\Olive"
git add database/olive_sms.db
git commit -m "Update SMS database"
git push
```

**Automated Sync** (add to `conductor_system.py`):
```python
import subprocess

def sync_to_github(self):
    """Sync database to GitHub after each message"""
    try:
        subprocess.run(['git', 'add', 'database/olive_sms.db'])
        subprocess.run(['git', 'commit', '-m', f'Auto-sync: {datetime.now()}'])
        subprocess.run(['git', 'push'])
    except Exception as e:
        logger.error(f"GitHub sync failed: {e}")
```

---

## 📈 Scaling Considerations

### Multiple Modems
To scale to multiple modems:
```python
# multi_conductor.py
modems = [
    {"port": "COM24", "db": "database/modem1.db"},
    {"port": "COM25", "db": "database/modem2.db"},
]

for modem in modems:
    thread = threading.Thread(target=run_conductor, args=(modem,))
    thread.start()
```

### High Volume
For high message volumes:
- Reduce `poll_interval` to 5 seconds
- Implement message prioritization
- Add message batching
- Use connection pooling

### Redundancy
For production reliability:
- Run multiple conductor instances (different machines)
- Implement health checks
- Add failover logic
- Monitor with external tools

---

## 🎓 Developer Quickstart

**5-Minute Setup**:
```bash
# 1. Clone/navigate to project
cd "C:\Dev\n8n budtenders\Olive"

# 2. Install dependencies
pip install pyserial

# 3. Update COM port in conductor_system.py (line 36)
# PORT = "COM24"  # Change to your COM port

# 4. Start conductor
python conductor_system.py

# 5. In another terminal, send test message
python conductor_system.py test +YOUR_NUMBER "Test"

# 6. In another terminal, watch database
python db_viewer.py
```

**Done!** Your conductor system is running and processing SMS messages.

---

## 📝 Summary

**What Makes This Architecture Special**:
1. ✅ **No COM port conflicts** - Polling architecture
2. ✅ **Bidirectional** - Send and receive seamlessly
3. ✅ **Database-driven** - All messages persisted
4. ✅ **Modem-agnostic** - Works with any AT-command modem
5. ✅ **Simple** - Single Python script, no frameworks
6. ✅ **Proven** - 95 messages processed successfully

**Key Files to Understand**:
- `conductor_system.py` - Main system logic
- `database/olive_sms.db` - SQLite database
- `start_conductor.bat` - Start script

**Critical Concept**: 
The conductor never holds the COM port for more than 2-3 seconds, making it accessible for other processes while still maintaining reliable bidirectional SMS communication.

---

## 📞 Production Deployment

**Recommended Setup**:
1. Run conductor as a Windows service (using NSSM)
2. Set up automatic database backups
3. Configure GitHub Actions for automated sync
4. Implement health monitoring (e.g., Uptime Kuma)
5. Add alerting for message failures

**Windows Service Setup**:
```bash
# Using NSSM (Non-Sucking Service Manager)
nssm install ConductorSMS "C:\Python\python.exe" "C:\Dev\n8n budtenders\Olive\conductor_system.py"
nssm start ConductorSMS
```

---

**Architecture designed and battle-tested by: Olive SMS System**
**Status**: Production-ready ✅
**Last updated**: September 30, 2025

