# SMSConductor + n8n.io Integration Guide

**Goal**: Connect local SMSConductor to cloud n8n.io for automated SMS workflows

---

## 🎯 Integration Architecture Options

### Option 1: REST API Bridge (Recommended)
**Best for**: Real-time integration, low latency

```
SMSConductor (Local) ←→ REST API Server ←→ n8n.io (Cloud)
```

### Option 2: Database Sync Service
**Best for**: Reliable data sync, offline resilience

```
SMSConductor (Local) → Database → Sync Service → n8n.io (Cloud)
```

### Option 3: Webhook + Queue System
**Best for**: Event-driven workflows, decoupled architecture

```
SMSConductor (Local) → Webhook → Queue → n8n.io (Cloud)
```

---

## 🚀 Option 1: REST API Bridge (Recommended)

### Architecture

```
┌─────────────────┐    HTTP/HTTPS    ┌─────────────────┐
│ SMSConductor    │ ←──────────────→ │ n8n.io          │
│ (Local)         │                  │ (Cloud)         │
│                 │                  │                 │
│ ┌─────────────┐ │                  │ ┌─────────────┐ │
│ │ REST API    │ │                  │ │ HTTP Request│ │
│ │ Server      │ │                  │ │ Node        │ │
│ └─────────────┘ │                  │ └─────────────┘ │
└─────────────────┘                  └─────────────────┘
```

### Implementation

#### Step 1: Create REST API Server

**File**: `Olive/api_server.py`

```python
#!/usr/bin/env python3
"""
SMSConductor REST API Server
Provides HTTP endpoints for n8n.io integration
"""

from flask import Flask, request, jsonify
import sqlite3
import json
import os
from datetime import datetime
import logging

app = Flask(__name__)

# Load configuration
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    with open(config_path, 'r') as f:
        return json.load(f)

config = load_config()
DB_PATH = config['database']['path']

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/api/messages/unread', methods=['GET'])
def get_unread_messages():
    """Get all unread incoming messages"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT id, phone_number, content, timestamp, modem_timestamp
                FROM messages 
                WHERE status = 'unread' AND direction = 'inbound'
                ORDER BY timestamp DESC
            """)
            messages = [dict(row) for row in cursor.fetchall()]
            
            return jsonify({
                'success': True,
                'count': len(messages),
                'messages': messages
            })
    except Exception as e:
        logger.error(f"Error getting unread messages: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/messages/mark-read', methods=['POST'])
def mark_message_read():
    """Mark a message as read"""
    try:
        data = request.get_json()
        message_id = data.get('message_id')
        
        if not message_id:
            return jsonify({'success': False, 'error': 'message_id required'}), 400
        
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                UPDATE messages 
                SET status = 'read', updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            """, (message_id,))
            conn.commit()
            
            return jsonify({'success': True, 'message': 'Message marked as read'})
    except Exception as e:
        logger.error(f"Error marking message as read: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/messages/send', methods=['POST'])
def queue_message():
    """Queue a message for sending"""
    try:
        data = request.get_json()
        phone_number = data.get('phone_number')
        message = data.get('message')
        
        if not phone_number or not message:
            return jsonify({'success': False, 'error': 'phone_number and message required'}), 400
        
        with sqlite3.connect(DB_PATH) as conn:
            timestamp = datetime.now().isoformat()
            conn.execute("""
                INSERT INTO messages 
                (phone_number, content, timestamp, status, direction)
                VALUES (?, ?, ?, ?, ?)
            """, (phone_number, message, timestamp, 'queued', 'outbound'))
            conn.commit()
            
            cursor = conn.execute("SELECT last_insert_rowid()")
            msg_id = cursor.fetchone()[0]
            
            return jsonify({
                'success': True,
                'message_id': msg_id,
                'status': 'queued'
            })
    except Exception as e:
        logger.error(f"Error queueing message: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system status"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM messages")
            total = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM messages WHERE status = 'unread'")
            unread = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM messages WHERE status = 'queued'")
            queued = cursor.fetchone()[0]
            
            return jsonify({
                'success': True,
                'status': {
                    'total_messages': total,
                    'unread_messages': unread,
                    'queued_messages': queued,
                    'timestamp': datetime.now().isoformat()
                }
            })
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'success': True, 'status': 'healthy'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
```

#### Step 2: Update Requirements

**File**: `Olive/requirements.txt`

```
pyserial>=3.5
requests>=2.31.0
flask>=2.3.0
```

#### Step 3: Create API Server Batch File

**File**: `Olive/start_api_server.bat`

```batch
@echo off
REM Script: start_api_server.bat
REM Purpose: Start REST API server for n8n.io integration
REM Part of: Conductor SMS System

echo ========================================
echo   SMSConductor API Server
echo ========================================
echo.

cd /d "%~dp0"

python api_server.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: API server exited with error code %ERRORLEVEL%
    pause
    exit /b %ERRORLEVEL%
)

pause
```

---

## 🔧 n8n.io Workflow Setup

### Workflow 1: Check for New Messages

**Trigger**: Schedule (every 30 seconds)

**Nodes**:
1. **Schedule Trigger** - Every 30 seconds
2. **HTTP Request** - GET `http://YOUR_IP:5001/api/messages/unread`
3. **IF** - Check if messages exist
4. **Process Messages** - For each message
5. **HTTP Request** - POST `http://YOUR_IP:5001/api/messages/mark-read`

**HTTP Request Configuration**:
```json
{
  "method": "GET",
  "url": "http://YOUR_LOCAL_IP:5001/api/messages/unread",
  "headers": {
    "Content-Type": "application/json"
  }
}
```

### Workflow 2: Send SMS from n8n

**Trigger**: Manual or webhook

**Nodes**:
1. **Webhook** - Receive phone + message
2. **HTTP Request** - POST to queue message
3. **Wait** - 10 seconds
4. **HTTP Request** - GET status to verify

**HTTP Request Configuration**:
```json
{
  "method": "POST",
  "url": "http://YOUR_LOCAL_IP:5001/api/messages/send",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "phone_number": "{{ $json.phone_number }}",
    "message": "{{ $json.message }}"
  }
}
```

---

## 🌐 Network Configuration

### Port Forwarding (Required)

**Router Configuration**:
- Port: 5001
- Protocol: TCP
- Internal IP: Your computer's IP
- External Port: 5001 (or custom)

**Find Your IP**:
```powershell
ipconfig | findstr "IPv4"
```

### Security Considerations

**Option A: Basic Auth** (Add to API server)
```python
from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    return username == 'n8n' and password == 'your_secure_password'

@app.route('/api/messages/unread')
@auth.login_required
def get_unread_messages():
    # ... existing code
```

**Option B: API Key** (Add to API server)
```python
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key != 'your-secret-api-key':
            return jsonify({'error': 'Invalid API key'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/messages/unread')
@require_api_key
def get_unread_messages():
    # ... existing code
```

---

## 🚀 Option 2: Database Sync Service

### Architecture

```
SMSConductor → SQLite → Sync Service → Cloud Database → n8n.io
```

### Implementation

**File**: `Olive/sync_service.py`

```python
#!/usr/bin/env python3
"""
Database Sync Service
Syncs local SQLite to cloud database for n8n.io access
"""

import sqlite3
import requests
import time
import json
from datetime import datetime

class DatabaseSyncService:
    def __init__(self, local_db_path, cloud_api_url, api_key):
        self.local_db_path = local_db_path
        self.cloud_api_url = cloud_api_url
        self.api_key = api_key
        self.last_sync = None
    
    def sync_to_cloud(self):
        """Sync unread messages to cloud database"""
        try:
            with sqlite3.connect(self.local_db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT * FROM messages 
                    WHERE status = 'unread' AND direction = 'inbound'
                    AND timestamp > ?
                """, (self.last_sync or '1970-01-01',))
                
                messages = [dict(row) for row in cursor.fetchall()]
                
                if messages:
                    # Send to cloud
                    response = requests.post(
                        f"{self.cloud_api_url}/messages",
                        headers={'Authorization': f'Bearer {self.api_key}'},
                        json={'messages': messages}
                    )
                    
                    if response.status_code == 200:
                        # Mark as synced
                        for msg in messages:
                            conn.execute("""
                                UPDATE messages 
                                SET status = 'synced' 
                                WHERE id = ?
                            """, (msg['id'],))
                        conn.commit()
                        
                        self.last_sync = datetime.now().isoformat()
                        print(f"Synced {len(messages)} messages")
                
        except Exception as e:
            print(f"Sync error: {e}")
    
    def sync_from_cloud(self):
        """Sync queued messages from cloud"""
        try:
            response = requests.get(
                f"{self.cloud_api_url}/messages/queued",
                headers={'Authorization': f'Bearer {self.api_key}'}
            )
            
            if response.status_code == 200:
                messages = response.json().get('messages', [])
                
                with sqlite3.connect(self.local_db_path) as conn:
                    for msg in messages:
                        conn.execute("""
                            INSERT INTO messages 
                            (phone_number, content, timestamp, status, direction)
                            VALUES (?, ?, ?, ?, ?)
                        """, (msg['phone_number'], msg['content'], 
                              msg['timestamp'], 'queued', 'outbound'))
                    conn.commit()
                    
                    if messages:
                        print(f"Queued {len(messages)} messages from cloud")
                
        except Exception as e:
            print(f"Sync error: {e}")
    
    def run(self):
        """Main sync loop"""
        while True:
            self.sync_to_cloud()  # Incoming messages
            self.sync_from_cloud()  # Outgoing messages
            time.sleep(30)  # Sync every 30 seconds

if __name__ == '__main__':
    sync = DatabaseSyncService(
        local_db_path='database/olive_sms.db',
        cloud_api_url='https://your-cloud-api.com',
        api_key='your-api-key'
    )
    sync.run()
```

---

## 🎯 Option 3: Webhook + Queue System

### Architecture

```
SMSConductor → Webhook → Cloud Queue → n8n.io
n8n.io → Cloud Queue → Webhook → SMSConductor
```

### Implementation

**File**: `Olive/webhook_client.py`

```python
#!/usr/bin/env python3
"""
Webhook Client for SMSConductor
Sends events to cloud webhook service
"""

import requests
import json
import time
from datetime import datetime

class WebhookClient:
    def __init__(self, webhook_url, api_key):
        self.webhook_url = webhook_url
        self.api_key = api_key
    
    def send_message_received(self, message_data):
        """Send message received event"""
        payload = {
            'event': 'message_received',
            'timestamp': datetime.now().isoformat(),
            'data': message_data
        }
        
        try:
            response = requests.post(
                self.webhook_url,
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                },
                json=payload
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Webhook error: {e}")
            return False
    
    def send_message_sent(self, message_data):
        """Send message sent event"""
        payload = {
            'event': 'message_sent',
            'timestamp': datetime.now().isoformat(),
            'data': message_data
        }
        
        try:
            response = requests.post(
                self.webhook_url,
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                },
                json=payload
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Webhook error: {e}")
            return False

# Add to conductor_system.py
def _save_incoming_message(self, phone_number, content, modem_index, modem_timestamp, msg_hash):
    """Save incoming message to database"""
    try:
        with sqlite3.connect(self.db_path, timeout=self.db_timeout) as conn:
            timestamp = datetime.now().isoformat()
            parsed_modem_ts = None
            
            if self.preserve_timestamps and modem_timestamp:
                parsed_modem_ts = self._parse_modem_timestamp(modem_timestamp)
            
            conn.execute("""
                INSERT INTO messages 
                (phone_number, content, timestamp, modem_timestamp, status, direction, modem_index, message_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (phone_number, content, timestamp, parsed_modem_ts, 'unread', 'inbound', modem_index, msg_hash))
            conn.commit()
            
            # Send webhook event
            if hasattr(self, 'webhook_client'):
                self.webhook_client.send_message_received({
                    'phone_number': phone_number,
                    'content': content,
                    'timestamp': timestamp
                })
                
    except Exception as e:
        logger.error(f"Error saving incoming message: {e}")
```

---

## 🏆 Recommended Approach

### For Production: Option 1 (REST API Bridge)

**Why**:
- ✅ Real-time integration
- ✅ Low latency
- ✅ Simple to implement
- ✅ Easy to debug
- ✅ Works with n8n.io webhooks

**Implementation Steps**:
1. Create `api_server.py` (provided above)
2. Add Flask to requirements.txt
3. Configure port forwarding (5001)
4. Set up n8n.io workflows
5. Add basic authentication
6. Test with sample messages

### Security Setup

**Add to `api_server.py`**:
```python
from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    return username == 'n8n' and password == 'your_secure_password'

# Protect all endpoints
@app.route('/api/messages/unread')
@auth.login_required
def get_unread_messages():
    # ... existing code
```

**n8n.io HTTP Request Configuration**:
```json
{
  "method": "GET",
  "url": "http://YOUR_IP:5001/api/messages/unread",
  "headers": {
    "Content-Type": "application/json",
    "Authorization": "Basic bjhuOnlvdXJfc2VjdXJlX3Bhc3N3b3Jk"
  }
}
```

---

## 🚀 Quick Start

1. **Create API server**: Copy `api_server.py` to `Olive/`
2. **Update requirements**: Add `flask>=2.3.0`
3. **Install Flask**: `pip install flask`
4. **Start API server**: `python api_server.py`
5. **Configure port forwarding**: Port 5001
6. **Set up n8n.io workflows**: Use provided examples
7. **Test integration**: Send test messages

---

**Next Steps**: Would you like me to create the API server file and help you set up the n8n.io workflows?

