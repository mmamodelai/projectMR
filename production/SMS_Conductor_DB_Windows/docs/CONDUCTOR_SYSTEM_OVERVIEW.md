# Conductor SMS System - Complete Overview

## 🚀 System Overview

The Conductor SMS System is a production-ready, AI-powered SMS and email communication platform designed for customer service and loyalty programs. The system combines hardware SMS capabilities with modern AI and cloud technologies to provide seamless customer interactions.

**Current Benchmark**: `MotaBot v4.3 SMS+Email.json` (Production Ready)

---

## 📋 Table of Contents

1. [System Architecture](#system-architecture)
2. [Core Components](#core-components)
3. [Communication Channels](#communication-channels)
4. [AI Capabilities](#ai-capabilities)
5. [Database & Data Management](#database--data-management)
6. [Integration Points](#integration-points)
7. [Hardware Requirements](#hardware-requirements)
8. [Software Stack](#software-stack)
9. [System Monitoring](#system-monitoring)
10. [Deployment Guide](#deployment-guide)
11. [API Access](#api-access)
12. [Troubleshooting](#troubleshooting)

---

## 🏗️ System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Customer      │    │   Conductor      │    │   AI System     │
│   SMS/Email     │◄──►│   SMS System     │◄──►│   (n8n + AI)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   Supabase DB    │
                       │   (Messages)     │
                       └──────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │  Google Sheets   │
                       │ (Customer Data)  │
                       └──────────────────┘
```

### Data Flow
1. **Inbound**: Customer SMS → Conductor → Supabase → n8n AI → Response
2. **Outbound**: AI Response → Supabase → Conductor → Customer SMS
3. **Email**: AI Decision → Gmail API → Customer Email
4. **Data Sync**: Google Sheets → n8n Data Tables → AI Tools

---

## 🔧 Core Components

### 1. Conductor SMS System (`Olive/conductor_system.py`)
- **Purpose**: Hardware SMS interface and message management
- **Hardware**: SIM7600G-H USB modem (COM24)
- **Features**:
  - Bidirectional SMS communication
  - Automatic message polling (5-second intervals)
  - GSM character sanitization
  - Long SMS splitting (≤150 chars)
  - Automatic retry with exponential backoff
  - COM port conflict resolution
  - Real-time status monitoring

### 2. n8n Workflow Engine
- **Workflow**: `MotaBot v4.3 SMS+Email.json`
- **Purpose**: AI orchestration and business logic
- **Features**:
  - 30-second polling for new messages
  - AI-powered conversation management
  - Multi-channel communication (SMS + Email)
  - Data integration with Google Sheets
  - Conversation history management

### 3. Supabase Database
- **Purpose**: Message storage and real-time sync
- **Tables**: `messages` (id, timestamp, direction, status, phone_number, content, retry_count)
- **Features**:
  - Real-time message queuing
  - Status tracking (unread, queued, sent, failed)
  - Message history and conversation tracking
  - RESTful API access

### 4. AI System (OpenRouter + Gemini)
- **Model**: `google/gemini-2.5-flash`
- **Purpose**: Natural language processing and response generation
- **Features**:
  - Conversation history awareness
  - Customer data integration
  - Multi-tool access (SMS, Email, Data lookup)
  - Personalized responses
  - Privacy-aware information sharing

---

## 📱 Communication Channels

### SMS (Primary Channel)
- **Hardware**: SIM7600G-H USB modem
- **Protocol**: AT commands over serial (115200 baud)
- **Features**:
  - Real-time bidirectional communication
  - GSM 7-bit character encoding
  - Automatic long message splitting
  - Delivery confirmation
  - Retry logic for failed messages

### Email (Secondary Channel)
- **Service**: Gmail API integration
- **Purpose**: Detailed information, summaries, receipts
- **Features**:
  - AI-driven email composition
  - Customer email lookup
  - Professional formatting
  - Spam filter avoidance (no emojis)

### Communication Decision Logic
```
Customer Request → AI Analysis → Channel Selection:
├── Simple query → SMS response
├── "Email me" → Email + SMS confirmation  
├── Long content → Email + SMS summary
└── Account info → SMS + Email option
```

---

## 🤖 AI Capabilities

### Core AI Features
- **Conversation Memory**: Full conversation history retrieval
- **Personalization**: Customer name, points, visit history
- **Multi-tool Access**: SMS, Email, Customer data, Budtender info
- **Privacy Protection**: Only shares customer's own information
- **Natural Language**: Conversational, friendly tone

### AI Tools Available
1. **Customers Data Points**: Points, visits, dispensary, budtender info
2. **Budtenders Data Points**: Performance data, sales attribution
3. **Budtenders DB 2025 Info**: Contact details, store information
4. **Gmail**: Email composition and sending

### AI Decision Making
- **Immediate Response**: Uses customer data tools on every interaction
- **Channel Selection**: Chooses SMS, Email, or both based on request
- **Content Adaptation**: Adjusts message length and format per channel
- **Error Handling**: Graceful fallbacks and retry logic

---

## 🗄️ Database & Data Management

### Supabase (Message Storage)
```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    direction TEXT CHECK (direction IN ('inbound', 'outbound')),
    status TEXT CHECK (status IN ('unread', 'queued', 'sent', 'failed')),
    phone_number TEXT,
    content TEXT,
    retry_count INTEGER DEFAULT 0,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Google Sheets Integration
- **Customer Data**: Points, visits, dispensary, budtender info
- **Budtender Data**: Performance metrics, contact information
- **Sync Frequency**: Every 10 minutes via n8n schedule trigger
- **Data Tables**: n8n internal data tables for AI tool access

### Data Flow
```
Google Sheets → n8n Data Tables → AI Tools → Customer Responses
```

---

## 🔌 Integration Points

### External APIs
- **Gmail API**: Email sending and composition
- **Google Sheets API**: Customer and budtender data
- **OpenRouter API**: AI model access (Gemini 2.5 Flash)
- **Supabase API**: Message storage and retrieval

### Internal APIs
- **Conductor API**: SMS hardware interface
- **n8n Webhooks**: Workflow triggers and data exchange
- **Database APIs**: Real-time message queuing

### Authentication
- **Gmail**: OAuth2 (Gmail account 2)
- **Google Sheets**: OAuth2 (Google Sheets account)
- **OpenRouter**: API Key authentication
- **Supabase**: API Key + Bearer token

---

## 🔧 Hardware Requirements

### Primary Hardware
- **SIM7600G-H USB Modem**: SMS communication hardware
- **USB Connection**: COM24 (configurable)
- **SIM Card**: Active cellular service with SMS capability
- **Computer**: Windows 10/11 with USB ports

### Hardware Configuration
```bash
# Modem Settings
Port: COM24
Baud Rate: 115200
Timeout: 5 seconds
Character Set: GSM 7-bit
SMS Format: Text mode (AT+CMGF=1)
```

### Hardware Monitoring
- **Health Checks**: Automatic modem connectivity verification
- **Signal Quality**: RSSI monitoring and reporting
- **Error Detection**: COM port conflicts and resolution
- **Status Reporting**: Real-time hardware status in logs

---

## 💻 Software Stack

### Core Applications
- **Python 3.8+**: Conductor system and utilities
- **n8n**: Workflow automation and AI orchestration
- **Supabase**: Cloud database and API
- **Gmail API**: Email service integration

### Python Dependencies
```python
# Core SMS System
pyserial>=3.5          # Serial communication
requests>=2.25         # HTTP API calls
sqlite3                # Local database (optional)
supabase>=2.0          # Supabase client

# GUI Applications  
tkinter                # Database manager GUI
threading              # Background operations
logging                # System logging
```

### n8n Nodes Used
- **Schedule Trigger**: Message polling (30s intervals)
- **HTTP Request**: Supabase API calls
- **Code**: JavaScript data processing
- **AI Agent**: OpenRouter/Gemini integration
- **Data Table Tool**: Customer data access
- **Gmail Tool**: Email sending
- **Google Sheets**: Data synchronization

---

## 📊 System Monitoring

### Real-time Monitoring
- **Conductor Logs**: `Olive/logs/conductor_system.log`
- **System Status**: `python conductor_system.py status`
- **Database Viewer**: `Olive/db_manager_gui.py`
- **Message Queue**: Supabase real-time dashboard

### Key Metrics
- **Message Throughput**: Messages per hour/day
- **Success Rate**: Sent vs Failed messages
- **Response Time**: AI processing latency
- **System Uptime**: Conductor cycle count
- **Error Rate**: Failed operations percentage

### Monitoring Tools
```bash
# System Status
cd Olive && python conductor_system.py status

# View Logs
Get-Content "Olive\logs\conductor_system.log" -Tail 50

# Database Manager
cd Olive && python db_manager_gui.py

# Test SMS
cd Olive && python conductor_system.py test +1234567890 "Test message"
```

---

## 🚀 Deployment Guide

### Prerequisites
1. **Hardware Setup**: SIM7600G-H modem connected to COM24
2. **Software Installation**: Python 3.8+, n8n, required packages
3. **API Keys**: Gmail, Google Sheets, OpenRouter, Supabase
4. **SIM Card**: Active cellular service

### Installation Steps

#### 1. Conductor System
```bash
# Clone repository
git clone <repository-url>
cd conductor

# Install Python dependencies
cd Olive
pip install -r requirements.txt

# Configure system
python conductor_system.py health
```

#### 2. n8n Workflow
```bash
# Import workflow
# File: n8nworkflows/MotaBot v4.3 SMS+Email.json

# Configure credentials:
# - Gmail account 2
# - Google Sheets account  
# - OpenRouter account
# - Supabase API keys
```

#### 3. Database Setup
```sql
-- Supabase table creation (automatic via Conductor)
-- Google Sheets data structure (pre-configured)
```

#### 4. System Startup
```bash
# Start Conductor
cd Olive && python conductor_system.py

# Start n8n workflow (import and activate)
# Monitor via database manager GUI
```

### Configuration Files
- **`Olive/config.json`**: System configuration
- **`n8nworkflows/MotaBot v4.3 SMS+Email.json`**: AI workflow
- **Credentials**: n8n credential management

---

## 🔑 API Access

### For Other Business Components

If you have other parts of your business that need to integrate with this system, here's what they need to know:

#### 1. Message API (Supabase)
```javascript
// Send message to customer
POST https://kiwmwoqrguyrcpjytgte.supabase.co/rest/v1/messages
Headers: {
  "apikey": "your-supabase-key",
  "Authorization": "Bearer your-supabase-key",
  "Content-Type": "application/json"
}
Body: {
  "phone_number": "+1234567890",
  "content": "Your message here",
  "status": "queued",
  "direction": "outbound"
}
```

#### 2. Customer Data API (Google Sheets)
```javascript
// Access customer information
// Via n8n Data Table Tools or direct Google Sheets API
// Fields: First_Name, Last_Name, Phone, Total_Points, 
//         Last_dispensary, Last_budtender, Email
```

#### 3. System Status API
```bash
# Check system health
GET /api/status  # (if API server enabled)
# Or direct database query for message counts
```

#### 4. Integration Requirements
For other business components to integrate:

**Required Data:**
- Customer phone numbers (E.164 format: +1234567890)
- Message content (text only, no emojis)
- Customer identification (phone number lookup)

**Available Data:**
- Customer points and visit history
- Budtender information and performance
- Message history and conversation context
- Real-time system status

**Integration Points:**
- **Supabase REST API**: Direct message queuing
- **n8n Webhooks**: Trigger workflows from external systems
- **Google Sheets API**: Customer data access
- **Conductor API**: Direct SMS sending (if API server enabled)

---

## 🔧 Troubleshooting

### Common Issues

#### 1. SMS Not Sending
```bash
# Check COM port
python -c "import serial.tools.list_ports; print([p.device for p in serial.tools.list_ports.comports()])"

# Test modem directly
python -c "import serial; s=serial.Serial('COM24',115200,timeout=5); s.write(b'AT\r\n'); print(s.read(100))"

# Check Conductor status
cd Olive && python conductor_system.py status
```

#### 2. AI Not Responding
- Check n8n workflow status
- Verify OpenRouter API key
- Check conversation history retrieval
- Monitor Supabase message queue

#### 3. Email Not Sending
- Verify Gmail credential in n8n
- Check customer email in data tables
- Monitor Gmail API quotas
- Review email content for spam triggers

#### 4. Database Issues
- Check Supabase connection
- Verify API keys and permissions
- Monitor database viewer GUI
- Check message status transitions

### System Health Checks
```bash
# Full system check
cd Olive
python conductor_system.py health
python conductor_system.py status

# Database check
python db_manager_gui.py

# Log analysis
Get-Content "logs\conductor_system.log" | Select-String -Pattern "ERROR|WARNING" -Context 2
```

### Performance Optimization
- **Message Polling**: Adjust intervals in config.json
- **AI Response Time**: Monitor OpenRouter API latency
- **Database Performance**: Index optimization in Supabase
- **Memory Usage**: Monitor Python process memory

---

## 📈 System Capabilities Summary

### What This System Can Do
✅ **Bidirectional SMS**: Send and receive text messages
✅ **AI-Powered Responses**: Natural language processing with conversation memory
✅ **Email Integration**: Send detailed emails to customers
✅ **Customer Data Access**: Points, visits, dispensary, budtender information
✅ **Multi-Channel Communication**: Choose SMS, Email, or both
✅ **Real-Time Processing**: 30-second response times
✅ **Automatic Retry**: Failed message recovery with exponential backoff
✅ **Message Management**: Long SMS splitting, GSM sanitization
✅ **System Monitoring**: Real-time status and health checks
✅ **Data Integration**: Google Sheets sync, Supabase storage
✅ **Privacy Protection**: Only shares customer's own information
✅ **Scalable Architecture**: Cloud-based, API-accessible

### Business Use Cases
- **Customer Service**: Automated responses to common questions
- **Loyalty Programs**: Points balance, visit history, rewards
- **Appointment Reminders**: SMS and email notifications
- **Marketing Campaigns**: Personalized messages based on customer data
- **Order Confirmations**: Multi-channel order status updates
- **Support Tickets**: Escalation to human agents when needed

### Integration Opportunities
- **POS Systems**: Real-time purchase data integration
- **CRM Systems**: Customer data synchronization
- **Marketing Platforms**: Campaign automation
- **Analytics Tools**: Message performance tracking
- **Mobile Apps**: Push notification alternatives
- **Web Applications**: Customer communication backend

---

## 📞 Support & Maintenance

### Regular Maintenance
- **Daily**: Check system status and message counts
- **Weekly**: Review failed messages and retry logic
- **Monthly**: Update customer data and budtender information
- **Quarterly**: Review AI performance and conversation quality

### System Updates
- **Workflow Updates**: Import new n8n workflow versions
- **AI Model Updates**: Monitor OpenRouter model performance
- **Database Migrations**: Supabase schema updates
- **Hardware Maintenance**: Modem health checks and firmware updates

### Contact Information
- **System Logs**: `Olive/logs/conductor_system.log`
- **Database Access**: Supabase dashboard
- **Workflow Management**: n8n interface
- **Hardware Issues**: Check COM port and modem connectivity

---

**Last Updated**: 2025-10-10  
**System Version**: MotaBot v4.3 SMS+Email  
**Status**: Production Ready ✅
