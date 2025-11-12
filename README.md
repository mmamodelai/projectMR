# Conductor V4.1 - Complete SMS & CRM System
**Version**: 4.1  
**Status**: Production  
**Last Updated**: October 12, 2025

---

## 🎯 Overview

**Conductor V4.1** is a modular, production-ready SMS management and customer relationship management system. It consists of three independent but integrated components:

1. **[Conductor SMS](#conductor-sms)** - SMS polling system with Supabase integration
2. **[MoTa CRM](#mota-crm)** - Customer relationship management with data viewers
3. **[MotaBot AI](#motabot-ai)** - Intelligent AI chatbot for n8n automation

---

## 📦 Project Structure

```
ConductorV4.1/
├── conductor-sms/          ← SMS management system
│   ├── conductor_system.py
│   ├── database/           ← Local SQLite DB
│   └── logs/
│
├── mota-crm/               ← CRM database & viewers
│   ├── viewers/            ← Desktop GUI applications
│   ├── import_tools/       ← CSV → Supabase import scripts
│   ├── docs/               ← Database schema & documentation
│   └── config/             ← Supabase credentials (.env)
│
├── motabot-ai/             ← AI workflows for n8n
│   ├── workflows/
│   │   ├── active/         ← Current production workflow
│   │   ├── Mota systems/   ← Specialized bot systems
│   │   │   ├── IC_Bot/     ← Internal Customers (Silverlake)
│   │   │   ├── IB_Bot/     ← Internal Budtenders (Planned)
│   │   │   └── Rex/        ← Receipt processing system
│   │   └── archive/        ← Previous versions
│   └── docs/
│
├── x_viewer.py             ← External Budtender Management
├── x_viewer_portable/      ← Portable client package
│
└── project cleanup/        ← Reorganization planning & archive
    ├── archive/            ← Old files (Cloudflare, diagnostics, etc.)
    └── backup/             ← Full system backup
```

---

## 🤖 Specialized Bot Systems

### **IC Bot** - Internal Customers (Silverlake CRM)
**Purpose**: Customer service bot for MOTA Silverlake customers  
**Status**: ✅ Production Ready  
**Location**: `motabot-ai/workflows/Mota systems/IC_Bot/`

**Features**:
- Customer profile lookup by phone number
- Complete transaction history from Supabase CRM
- Personalized product recommendations
- Real-time inventory checking
- Purchase pattern analysis

**Quick Start**:
```powershell
# Import workflow into n8n
motabot-ai/workflows/Mota systems/IC_Bot/ICworking1_v2.0.json
```

---

### **X-Viewer** - External Budtender Management
**Purpose**: Track and manage external budtenders from other dispensaries  
**Status**: ✅ Production Ready  
**Location**: `x_viewer.py` + `x_viewer_portable/`

**Features**:
- 524 budtenders from 112 dispensaries
- Live search and filtering
- Points system management
- Portable client package
- Performance tracking

**Quick Start**:
```powershell
# Launch main viewer
.\start_x_viewer.bat

# Launch portable version
.\start_x_viewer_portable.bat
```

---

### **IB Bot** - Internal Budtenders (Staff Coaching)
**Purpose**: Real-time performance coaching for MOTA Silverlake budtenders  
**Status**: 🚧 Planned - Not Yet Built  
**Location**: `motabot-ai/workflows/Mota systems/IB_Bot/`

**Planned Features**:
- Real-time performance tracking via Blaze POS
- Mid-shift coaching messages
- Upsell suggestions and training
- Performance analytics and recognition
- Team goal tracking

**Requirements**: Blaze POS API access, database schema design

---

### **REX System** - Receipt Processing
**Purpose**: Process customer receipts and award loyalty points  
**Status**: ✅ Production Ready  
**Location**: `motabot-ai/workflows/Mota systems/Rex/`

**Features**:
- Receipt photo processing
- Automatic MOTA product detection
- Points calculation (1 point per $1 spent)
- Budtender rewards (10x customer points)
- SMS and email confirmations

---

## 🚀 Quick Start

### **1. Conductor SMS** (SMS Management)

**What it does**: Polls a SIM7600G-H modem every 5 seconds to receive SMS, stores them in Supabase, and sends queued messages.

**Start the system**:
```powershell
cd conductor-sms
.\start_conductor.bat
```

**View SMS messages** (launch database viewer):
```powershell
.\start_SMSconductor_DB.bat
```
*Shows all SMS messages from Supabase with stats, right-click to edit/delete/change status*

**Check status**:
```powershell
python conductor_system.py status
```

**Send test message**:
```powershell
.\test_conductor.bat +16199773020 "Test message"
```

**📊 SMS Database**: Stores inbound/outbound messages in Supabase (`messages` table)

**📖 Documentation**: See [`conductor-sms/README.md`](conductor-sms/README.md)

---

### **2. MoTa CRM** (Customer Database & Viewers)

**What it does**: Provides desktop GUI viewers for managing customers, transactions, and inventory from Supabase.

#### **CRM Integrated Viewer v2** (OPTIMIZED - RECOMMENDED) ⚡
```powershell
cd mota-crm\viewers
.\start_crm_optimized.bat
```
*Single unified interface with **NEW OPTIMIZED VIEWS** - 10-50x faster than v1!*

**Data it displays**:
- **Customers** (10,047 records): ALL customers with instant search
- **Customer Context**: Favorite products, churn risk, preferences (uses `customer_sms_context` view)
- **Transactions** (186,394 records): Cascading query - only loads selected customer's transactions
- **Transaction Items** (114,136 records): Cascading query - only loads selected transaction's items
- **Product Details**: THC/CBD content, strain type, effects, pricing - on-demand loading

**🚀 Performance**: 
- Initial load: 10,047 customers in ~2-3 seconds
- Customer context: <100ms (1 query vs 5)
- Transactions: <200ms (only selected customer)
- Items: <100ms (only selected transaction)

#### **Individual Viewers** (optional)
```powershell
.\start_all_viewers.bat
```
*Launches separate windows for customers, inventory, and transactions*

**Import new data** (CSV → Supabase):
```powershell
cd ..\import_tools
python import_customers_to_supabase.py
```

**📊 Supabase CRM Database**: 
- **5 tables**: `customers`, `transactions`, `transaction_items`, `products`, `staff`
- **4 optimized views**: `customer_sms_context`, `customer_product_affinity`, `customer_visit_patterns`, `win_back_priority_queue`
- **Full details**: See [`SUPABASE_MIGRATIONS_COMPLETE.md`](SUPABASE_MIGRATIONS_COMPLETE.md)

**📖 Documentation**: See [`mota-crm/README.md`](mota-crm/README.md)

---

### **3. MotaBot AI** (Intelligent Chatbot)

**What it does**: n8n workflow that reads incoming SMS, uses AI to generate responses, queries CRM for customer data, and sends replies.

**Current Version**: `MotaBot wDB v5.100 COMPATIBLE.json`

**How to use**:
1. Import workflow into n8n:
   ```
   motabot-ai/workflows/active/MotaBot wDB v5.100 COMPATIBLE.json
   ```
2. Configure Supabase connection in n8n
3. Activate workflow
4. Send SMS → AI responds automatically!

**Features**:
- Reads SMS from Supabase `messages` table
- Queries CRM for customer data (name, VIP status, visits, lifetime value)
- Uses AI to generate personalized responses
- Queues response in Supabase for Conductor to send
- Supports both SMS and email

**📖 Documentation**: See [`motabot-ai/README.md`](motabot-ai/README.md)

---

## 📊 Database Viewers

**Complete guide to all GUI viewers, what data they display, and how to use them**:

👉 **See [`DATABASE_VIEWERS_GUIDE.md`](DATABASE_VIEWERS_GUIDE.md)** for full details

**Quick Summary**:
| Viewer | Data Source | Purpose |
|--------|-------------|---------|
| **SMS Conductor DB** | Supabase `messages` | View/edit/delete SMS, change status |
| **CRM Integrated** | Supabase CRM (4 tables) | Unified customer, transactions, products view |
| **Individual Viewers** | Supabase CRM | Separate windows for customers/inventory/transactions |

---

## 🔗 System Integration

### How the 3 Components Work Together:

```
┌─────────────────────────────────────────────────────────────────┐
│                         SUPABASE                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  messages   │  │  customers  │  │transactions │             │
│  │             │  │             │  │             │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└───────▲──────▲──────────▲──────────────▲────────────────────────┘
        │      │          │              │
        │      │          │              │
   ┌────┴──┐   │     ┌────┴────┐    ┌───┴────┐
   │  SMS  │   │     │ MotaBot │    │  CRM   │
   │ Write │   │     │  Query  │    │ Viewers│
   └───────┘   │     └─────────┘    └────────┘
               │
          ┌────┴────┐
          │ MotaBot │
          │  Write  │
          └────┬────┘
               │
        ┌──────┴────────┐
        │  Conductor    │
        │  Read & Send  │
        └───────────────┘
```

**Data Flow**:
1. **Incoming SMS** → Conductor receives → writes to Supabase `messages` table
2. **MotaBot** → reads unread messages → queries CRM → generates AI response → writes to `messages` (status: queued)
3. **Conductor** → reads queued messages → sends via modem → updates status to sent

**All 3 components can run independently!**

---

## ⚙️ Configuration

### Supabase Setup

All 3 components connect to the same Supabase project:

**URL**: `https://kiwmwoqrguyrcpjytgte.supabase.co`

**Tables**:
- `messages` - SMS inbox/outbox (Conductor + MotaBot)
- `customers` - Customer CRM data (CRM + MotaBot)
- `transactions` - Purchase history (CRM + MotaBot)
- `transaction_items` - Line items (CRM)
- `products` - Inventory (CRM + MotaBot)
- `staff` - Budtender data (CRM + MotaBot)

**Credentials**:
- **Conductor**: `conductor-sms/config.json`
- **CRM Viewers**: `mota-crm/config/.env`
- **MotaBot**: Stored in n8n credentials

---

## 🛠️ Requirements

### Software:
- **Python 3.9+** (for Conductor & CRM)
- **n8n** (for MotaBot workflows)
- **Supabase account** (cloud database)

### Hardware:
- **SIM7600G-H USB Modem** (for SMS)
- **Windows 10/11** (scripts optimized for Windows)

### Python Packages:
See individual project requirements:
- `conductor-sms/requirements.txt`
- `mota-crm/viewers/requirements.txt` (uses supabase-py, tkinter)

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| **[Conductor SMS README](conductor-sms/README.md)** | SMS system setup & usage |
| **[MoTa CRM README](mota-crm/README.md)** | CRM viewers & import tools |
| **[MotaBot AI README](motabot-ai/README.md)** | AI workflow configuration |
| **[Database Schema](mota-crm/docs/SUPABASE_SCHEMA_DESIGN.md)** | Complete DB structure |
| **[System Status](mota-crm/docs/SYSTEM_STATUS.md)** | Data completeness & health |
| **[Reorganization Plan](project cleanup/REORGANIZATION_PLAN.md)** | How this structure was created |

---

## 🧪 Testing

### Test Conductor SMS:
```powershell
cd conductor-sms
python conductor_system.py status
.\test_conductor.bat +1234567890 "Test message"
```

### Test CRM Viewer:
```powershell
cd mota-crm\viewers
pythonw crm_integrated.py
# Search for a customer, view their transactions
```

### Test MotaBot:
1. Send SMS to your modem's number
2. Check n8n workflow execution logs
3. Verify AI response is queued in Supabase
4. Conductor sends the response

---

## 🐛 Troubleshooting

### Conductor not receiving SMS?
- Check modem connection: `python modem_probe.py`
- Check COM port in `config.json` (default: COM24)
- Check Supabase connection

### CRM viewer not loading data?
- Check `.env` file in `mota-crm/config/`
- Verify Supabase credentials
- Check internet connection

### MotaBot not responding?
- Verify n8n workflow is active
- Check Supabase credentials in n8n
- Check AI model quota/limits
- Review n8n execution logs

---

## 📊 Current System Status

**Last System Test**: October 11, 2025

| Component | Status | Notes |
|-----------|--------|-------|
| Conductor SMS | ✅ Operational | 14 messages, 6 sent, 0 failed |
| CRM Viewers | ✅ Operational | All viewers functional |
| MotaBot v5.100 | ✅ Operational | CRM integration working |
| Supabase DB | ✅ Healthy | 100% data completeness |

---

## 🔥 Blaze API Integration (NEW!)

### **Status**: 🚧 Planning Phase - API Access Granted
**Purpose**: Replace CSV imports with real-time data from Blaze POS system

### **📋 Integration Rules & Best Practices**

#### **💰 Pricing Tiers**
- **Tier 1**: $100/month, 250K calls, $0.0006 per overage
- **Tier 2**: $250/month, 1.5M calls, $0.0002 per overage  
- **Tier 3**: $500/month, 10M calls, $0.0001 per overage

#### **⚠️ Rate Limits**
- **MAX**: 10,000 calls per 5 minutes
- **Exceed = throttling or key disabled**

#### **📅 Sync Schedule Requirements**
- **Historical Transactions**: Hourly or nightly (batch processing)
- **Members (Customers)**: Hourly or nightly (use `modified` date)
- **Inventory (Products)**: No more than every 5 minutes (incremental updates)

#### **🚫 Restrictions**
- **No payment data** through API without Blaze consent
- **No third-party data sharing** for commercial use
- **Partner key** only for your dispensary locations

### **🎯 Implementation Strategy**

#### **Phase 1: Discovery** (Current)
- [ ] Test API authentication
- [ ] Map Blaze data structure to Supabase schema
- [ ] Identify data gaps/inconsistencies

#### **Phase 2: Hybrid Integration**
- [ ] Keep existing historical data (22K customers)
- [ ] Use Blaze API for new transactions going forward
- [ ] Update calculated fields (lifetime_value, days_since_last_visit)
- [ ] Implement incremental sync using `modified` dates

#### **Phase 3: Full Migration**
- [ ] Replace CSV imports with API sync
- [ ] Implement real-time updates
- [ ] Deprecate old import processes

### **🔧 Technical Implementation**

#### **API Endpoints We Need**
- **Members**: `/api/v1/members` - Customer data
- **Orders**: `/api/v1/orders` - Transaction data  
- **Products**: `/api/v1/products` - Product catalog
- **Loyalty**: `/api/v1/loyalty` - Points and rewards

#### **Optimization Strategy**
- **Use modified dates** to avoid re-fetching unchanged data
- **Batch API calls** efficiently
- **Cache data locally** to reduce API calls
- **Monitor call volume** to stay under limits
- **Start with Tier 1** ($100/month, 250K calls)

### **📊 Expected Benefits**
- ✅ **Live data** (no more stale calculated fields)
- ✅ **Real-time updates** (no more CSV imports)
- ✅ **Accurate calculations** (no more data inconsistencies)
- ✅ **Automated sync** (no more manual processes)

### **📁 Documentation**
- **API Guide**: `docs/BLAZEAPI/README.md`
- **Key Endpoints**: `docs/BLAZEAPI/blaze_api_summary.md`
- **Complete Spec**: `docs/BLAZEAPI/swagger.json` (23,874 lines)
- **Usage Rules**: `docs/BLAZEAPI/rules from blaze.md`

---

## 🔄 Recent Changes

### v4.1 - October 23, 2025
**Blaze API Integration Planning**:
- Added comprehensive Blaze API documentation
- Organized API docs in `docs/BLAZEAPI/` structure
- Created AI agent guide for API usage
- Defined integration rules and best practices
- Planned hybrid migration strategy (keep historical + use API)

**IC Viewer Improvements**:
- Renamed CRM Integrated Viewer to "IC Viewer - Internal Customer System"
- Fixed Revenue by Brand calculation bug (was showing $96.73 instead of ~$1,016)
- Updated customer preferences calculation (favorite category, location, payment)
- Improved data consistency between panels

**Data Analysis**:
- Completed duplicate analysis (found 1,943 duplicate groups)
- Identified data inconsistencies in customer calculated fields
- Discovered stale data issues (days_since_last_visit, lifetime_value)
- Confirmed need for real-time API integration

### v4.1 - October 11, 2025
**Major Reorganization**:
- Split monolithic project into 3 modular components
- Removed Cloudflare tunnel files (65MB saved)
- Archived API server (using Supabase directly)
- Archived diagnostic scripts
- Created comprehensive documentation
- Removed large CSV files from git (82MB saved)

**Fixed**:
- Transaction items data (114,136 items, 100% complete)
- CRM viewer sortable columns
- Right-click editing in CRM viewer
- Product intelligence panel

**Added**:
- MotaBot v5.100 with CRM data injection
- Integrated CRM viewer with 4-column layout
- On-demand data loading for efficiency
- Desktop shortcuts for quick access

---

## 📧 Support & Contact

**GitHub**: https://github.com/mmamodelai/ConductorV4.1  
**Issues**: https://github.com/mmamodelai/ConductorV4.1/issues

---

## 📜 License

Proprietary - MMA Model AI  
© 2025 All Rights Reserved

---

**🎉 Conductor V4.1 is production-ready! Each component runs independently but integrates seamlessly via Supabase.**
