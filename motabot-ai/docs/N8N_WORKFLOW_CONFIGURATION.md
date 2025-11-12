# n8n.io Workflow Configuration Guide

**SMSConductor + n8n.io Integration Workflows**

---

## 🚀 Quick Setup

### Prerequisites
1. **SMSConductor API Server** running on port 5001
2. **Port forwarding** configured (port 5001)
3. **n8n.io account** (cloud version)
4. **Your public IP** address

### Find Your Public IP
```powershell
# Windows PowerShell
Invoke-RestMethod -Uri "https://api.ipify.org"
```

---

## 📋 Workflow 1: Monitor Incoming Messages

**Purpose**: Check for new incoming SMS messages every 30 seconds

### Node Configuration

#### 1. Schedule Trigger
```json
{
  "rule": {
    "interval": [
      {
        "field": "seconds",
        "secondsInterval": 30
      }
    ]
  }
}
```

#### 2. HTTP Request - Get Unread Messages
```json
{
  "method": "GET",
  "url": "http://YOUR_PUBLIC_IP:5001/api/messages/unread",
  "headers": {
    "Content-Type": "application/json"
  },
  "timeout": 10000
}
```

#### 3. IF Node - Check for Messages
```json
{
  "conditions": {
    "options": {
      "caseSensitive": true,
      "leftValue": "",
      "typeValidation": "strict"
    },
    "conditions": [
      {
        "id": "condition1",
        "leftValue": "={{ $json.count }}",
        "rightValue": 0,
        "operator": {
          "type": "number",
          "operation": "gt"
        }
      }
    ],
    "combinator": "and"
  }
}
```

#### 4. Split In Batches - Process Each Message
```json
{
  "batchSize": 1,
  "options": {}
}
```

#### 5. HTTP Request - Mark as Read
```json
{
  "method": "POST",
  "url": "http://YOUR_PUBLIC_IP:5001/api/messages/mark-read",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "message_id": "={{ $json.messages[0].id }}"
  }
}
```

#### 6. Process Message (Your Logic)
- **Phone Number**: `{{ $json.messages[0].phone_number }}`
- **Content**: `{{ $json.messages[0].content }}`
- **Timestamp**: `{{ $json.messages[0].timestamp }}`

---

## 📤 Workflow 2: Send SMS from n8n

**Purpose**: Send SMS messages from n8n workflows

### Node Configuration

#### 1. Webhook Trigger
```json
{
  "httpMethod": "POST",
  "path": "send-sms",
  "responseMode": "responseNode"
}
```

#### 2. HTTP Request - Queue Message
```json
{
  "method": "POST",
  "url": "http://YOUR_PUBLIC_IP:5001/api/messages/send",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "phone_number": "={{ $json.phone_number }}",
    "message": "={{ $json.message }}"
  }
}
```

#### 3. Respond to Webhook
```json
{
  "respondWith": "json",
  "responseBody": {
    "success": "={{ $json.success }}",
    "message_id": "={{ $json.message_id }}",
    "status": "={{ $json.status }}"
  }
}
```

### Webhook Usage
**URL**: `https://your-n8n-instance.com/webhook/send-sms`

**Payload**:
```json
{
  "phone_number": "+16199773020",
  "message": "Hello from n8n!"
}
```

---

## 📊 Workflow 3: System Status Monitor

**Purpose**: Monitor SMSConductor system health

### Node Configuration

#### 1. Schedule Trigger (Every 5 minutes)
```json
{
  "rule": {
    "interval": [
      {
        "field": "minutes",
        "minutesInterval": 5
      }
    ]
  }
}
```

#### 2. HTTP Request - Get Status
```json
{
  "method": "GET",
  "url": "http://YOUR_PUBLIC_IP:5001/api/status",
  "headers": {
    "Content-Type": "application/json"
  }
}
```

#### 3. IF Node - Check for Issues
```json
{
  "conditions": {
    "options": {
      "caseSensitive": true,
      "leftValue": "",
      "typeValidation": "strict"
    },
    "conditions": [
      {
        "id": "condition1",
        "leftValue": "={{ $json.status.queued_messages }}",
        "rightValue": 10,
        "operator": {
          "type": "number",
          "operation": "gt"
        }
      }
    ],
    "combinator": "or"
  }
}
```

#### 4. Send Alert (Slack/Email/Webhook)
Configure your preferred notification method.

---

## 🔧 Advanced Workflow: Auto-Reply System

**Purpose**: Automatically reply to incoming messages

### Node Configuration

#### 1. Schedule Trigger (Every 30 seconds)
```json
{
  "rule": {
    "interval": [
      {
        "field": "seconds",
        "secondsInterval": 30
      }
    ]
  }
}
```

#### 2. HTTP Request - Get Unread Messages
```json
{
  "method": "GET",
  "url": "http://YOUR_PUBLIC_IP:5001/api/messages/unread",
  "headers": {
    "Content-Type": "application/json"
  }
}
```

#### 3. IF Node - Check for Messages
```json
{
  "conditions": {
    "options": {
      "caseSensitive": true,
      "leftValue": "",
      "typeValidation": "strict"
    },
    "conditions": [
      {
        "id": "condition1",
        "leftValue": "={{ $json.count }}",
        "rightValue": 0,
        "operator": {
          "type": "number",
          "operation": "gt"
        }
      }
    ],
    "combinator": "and"
  }
}
```

#### 4. Split In Batches
```json
{
  "batchSize": 1,
  "options": {}
}
```

#### 5. IF Node - Check Message Content
```json
{
  "conditions": {
    "options": {
      "caseSensitive": false,
      "leftValue": "",
      "typeValidation": "strict"
    },
    "conditions": [
      {
        "id": "condition1",
        "leftValue": "={{ $json.messages[0].content }}",
        "rightValue": "help",
        "operator": {
          "type": "string",
          "operation": "contains"
        }
      }
    ],
    "combinator": "or"
  }
}
```

#### 6. HTTP Request - Send Auto-Reply
```json
{
  "method": "POST",
  "url": "http://YOUR_PUBLIC_IP:5001/api/messages/send",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "phone_number": "={{ $json.messages[0].phone_number }}",
    "message": "Thank you for your message! We'll get back to you soon."
  }
}
```

#### 7. HTTP Request - Mark Original as Read
```json
{
  "method": "POST",
  "url": "http://YOUR_PUBLIC_IP:5001/api/messages/mark-read",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "message_id": "={{ $json.messages[0].id }}"
  }
}
```

---

## 🔐 Security Configuration

### Option 1: Basic Authentication

#### Update API Server
Add to `api_server.py`:
```python
from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    return username == 'n8n' and password == 'your_secure_password'

# Protect endpoints
@app.route('/api/messages/unread')
@auth.login_required
def get_unread_messages():
    # ... existing code
```

#### Update n8n HTTP Requests
Add to headers:
```json
{
  "Authorization": "Basic bjhuOnlvdXJfc2VjdXJlX3Bhc3N3b3Jk"
}
```

### Option 2: API Key Authentication

#### Update API Server
```python
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key != 'your-secret-api-key':
            return jsonify({'error': 'Invalid API key'}), 401
        return f(*args, **kwargs)
    return decorated_function
```

#### Update n8n HTTP Requests
Add to headers:
```json
{
  "X-API-Key": "your-secret-api-key"
}
```

---

## 🧪 Testing Workflows

### Test Incoming Message Flow
1. **Send SMS** to your modem
2. **Check n8n logs** for workflow execution
3. **Verify message** appears in database
4. **Confirm message** marked as read

### Test Outgoing Message Flow
1. **Trigger webhook** with test data
2. **Check SMSConductor** for queued message
3. **Verify message** sent successfully
4. **Confirm status** updated in database

### Test Error Handling
1. **Stop API server** temporarily
2. **Run workflow** - should handle errors gracefully
3. **Restart API server**
4. **Verify recovery** works correctly

---

## 📈 Monitoring & Alerts

### Key Metrics to Monitor
- **Unread message count** (should not exceed 50)
- **Queued message count** (should not exceed 20)
- **Failed message count** (should be 0)
- **API response time** (should be < 2 seconds)

### Alert Conditions
- **High message backlog** (> 50 unread)
- **API server down** (health check fails)
- **Failed messages** (> 5 in last hour)
- **Slow response** (> 5 seconds)

### Notification Channels
- **Slack**: Real-time alerts
- **Email**: Daily summaries
- **Webhook**: Custom integrations
- **SMS**: Critical alerts (via SMSConductor)

---

## 🚀 Production Deployment

### Checklist
- [ ] **Port forwarding** configured
- [ ] **API server** running as service
- [ ] **Security** (auth/API key) enabled
- [ ] **Monitoring** workflows active
- [ ] **Error handling** tested
- [ ] **Backup** procedures in place
- [ ] **Documentation** updated

### Performance Optimization
- **Batch processing** for multiple messages
- **Connection pooling** for HTTP requests
- **Caching** for status checks
- **Rate limiting** for webhook endpoints

---

## 🔧 Troubleshooting

### Common Issues

#### API Server Not Responding
```powershell
# Check if API server is running
netstat -an | findstr :5001

# Check API server logs
Get-Content logs\api_server.log -Tail 20
```

#### Port Forwarding Issues
```powershell
# Test from external network
Invoke-RestMethod -Uri "http://YOUR_PUBLIC_IP:5001/api/health"
```

#### n8n Workflow Errors
- Check **HTTP request** configuration
- Verify **URL** and **headers**
- Test **authentication** credentials
- Review **error logs** in n8n

### Debug Mode
Enable debug logging in API server:
```python
app.run(host='0.0.0.0', port=5001, debug=True)
```

---

## 📚 Next Steps

1. **Set up workflows** using provided configurations
2. **Test integration** with sample messages
3. **Configure monitoring** and alerts
4. **Implement security** (auth/API key)
5. **Deploy to production** with monitoring
6. **Document custom** workflows
7. **Train team** on n8n integration

---

**Ready to integrate SMSConductor with n8n.io!** 🚀
