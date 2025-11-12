# Database Viewers Guide
**Version**: 1.0  
**Last Updated**: October 12, 2025

---

## Overview

This document describes all database viewer applications in the Conductor V4.1 system, what data they display, and how to launch them.

---

## 📱 SMS Conductor DB Viewer

**Location**: `conductor-sms/SMSconductor_DB.py`

**Launch**:
```powershell
cd conductor-sms
.\start_SMSconductor_DB.bat
```

### What It Displays

**Database**: Supabase SMS Database  
**Table**: `messages`

| Column | Description |
|--------|-------------|
| **ID** | Message UUID (first 8 chars) |
| **Phone** | Customer phone number (E.164 format) |
| **Direction** | `inbound` or `outbound` |
| **Status** | `sent`, `queued`, `failed`, `unread`, `read` |
| **Content** | SMS message text (first 50 chars, click for full) |
| **Timestamp** | When message was sent/received |

### Features
- 🎨 **Color-coded rows**:
  - Green = `sent`
  - Red = `failed`
  - Yellow = `queued`
  - Blue = `unread`
- 🖱️ **Right-click menu**:
  - Edit message content
  - Delete message
  - Change status (unread, queued, sent, failed, read)
- 📊 **Live statistics**: Total, Sent, Queued, Failed, Unread
- 🔍 **Detail panel**: Click any message to see full content
- 🔄 **Refresh button**: Reload messages from database

### Use Cases
- Monitor incoming SMS messages
- Check outbound message delivery status
- Manually edit message content before sending
- Debug failed messages
- View conversation history with customers

---

## 🏢 CRM Integrated Viewer (RECOMMENDED)

**Location**: `mota-crm/viewers/crm_integrated.py`

**Launch**:
```powershell
cd mota-crm\viewers
.\start_crm_integrated.bat
```

### What It Displays

**Database**: Supabase CRM Database  
**Tables**: `customers`, `transactions`, `transaction_items`, `products`

#### Panel 1: Customers (3,186 records)

| Column | Description |
|--------|-------------|
| **ID** | Customer UUID (first 8 chars) |
| **Name** | Customer full name |
| **Phone** | Primary phone number |
| **Email** | Email address |
| **VIP** | VIP status (New, Casual, Regular, VIP) |
| **Visits** | Total visit count |
| **Lifetime Value** | Total spend ($) |
| **Last Visit** | Most recent transaction date |
| **Churn Risk** | Risk level (Low, Medium, High) |

**Sortable**: Click column headers to sort by any field

#### Panel 2: Transactions (186,394 records)

Shows transactions for **selected customer only**:

| Column | Description |
|--------|-------------|
| **Transaction ID** | Transaction number |
| **Date** | Transaction date |
| **Total** | Total amount ($) |
| **Payment Method** | Cash, Card, etc. |
| **Staff** | Budtender name |
| **Location** | Store location |

#### Panel 3: Transaction Items (114,136 records)

Shows items for **selected transaction only**:

| Column | Description |
|--------|-------------|
| **Product SKU** | Product identifier |
| **Product Name** | Product name |
| **Quantity** | Units purchased |
| **Unit Price** | Price per unit ($) |
| **Total** | Line item total ($) |
| **Discount** | Discount applied ($) |

#### Panel 4: Product Details

Shows details for **selected product only**:

| Field | Description |
|-------|-------------|
| **Name** | Full product name |
| **Category** | Product category |
| **Brand** | Manufacturer |
| **THC Content** | THC percentage/mg |
| **CBD Content** | CBD percentage/mg |
| **Strain Type** | Indica, Sativa, Hybrid |
| **Effects** | Expected effects |
| **Pricing** | Unit cost and retail price |
| **Vendor** | Supplier name |
| **Stock Status** | In stock, low, out of stock |
| **Stock Age** | Days since last restock |

### Features
- 🔗 **Linked data**: Select customer → see their transactions → see items → see product details
- 🔍 **Customer search**: Find by name or phone number
- ✏️ **Right-click edit**: Edit customer fields (name, phone, VIP status)
- 📊 **Smart loading**: Only loads data when needed (fast and efficient)
- 📈 **Analytics**: VIP status, churn risk, lifetime value auto-calculated

### Use Cases
- Look up customer purchase history
- Analyze customer spending patterns
- Identify VIP customers
- Check product popularity
- Research product details (THC/CBD, effects)
- Find customers at risk of churning
- Verify transaction accuracy

---

## 📦 Individual CRM Viewers

**Location**: `mota-crm/viewers/`

**Launch all**:
```powershell
cd mota-crm\viewers
.\start_all_viewers.bat
```

### Customer Viewer
**File**: `customer_viewer_fixed.py`

Displays full `customers` table in a single window. Good for:
- Bulk customer analysis
- Exporting customer lists
- Quick customer lookup

### Inventory Viewer
**File**: `inventory_viewer_fixed.py`

Displays full `products` table (3,299 products). Good for:
- Product catalog browsing
- Stock level monitoring
- Product search
- Random sampling (1,000 random products)

### Transaction Viewer
**File**: `transaction_viewer_fixed.py`

Displays full `transactions` table (186,394 records). Good for:
- Daily sales analysis
- Payment method breakdown
- Revenue tracking
- Store performance comparison

---

## 🗂️ Viewer Comparison

| Feature | SMS Conductor DB | CRM Integrated | Individual Viewers |
|---------|------------------|----------------|-------------------|
| **Database** | Supabase SMS | Supabase CRM | Supabase CRM |
| **Tables** | `messages` | 4 linked tables | 1 table each |
| **Records** | ~14 messages | 300K+ records | Varies by viewer |
| **Edit** | ✅ Right-click | ✅ Right-click | ❌ View only |
| **Delete** | ✅ Yes | ❌ No | ❌ No |
| **Search** | ❌ No | ✅ Customer search | ❌ No |
| **Linked Data** | ❌ No | ✅ Yes | ❌ No |
| **Best For** | SMS management | Customer research | Bulk analysis |

---

## 🚀 Quick Launch Commands

### From Root Directory

**SMS Conductor DB Viewer**:
```powershell
cd conductor-sms && .\start_SMSconductor_DB.bat
```

**CRM Integrated Viewer**:
```powershell
cd mota-crm\viewers && .\start_crm_integrated.bat
```

**All CRM Viewers**:
```powershell
cd mota-crm\viewers && .\start_all_viewers.bat
```

---

## 🔧 Requirements

All viewers require:
- Python 3.9+
- `tkinter` (GUI framework, included with Python)
- `supabase` Python client
- Valid Supabase credentials in `config.json` or `.env`

Install dependencies:
```powershell
pip install supabase
```

---

## 🐛 Troubleshooting

### Viewer Won't Launch

**Check Python**:
```powershell
python --version
```
Should be 3.9 or higher.

**Check Supabase credentials**:
- SMS viewers: `conductor-sms/config.json`
- CRM viewers: `mota-crm/config/.env`

### "Invalid API Key"

Update Supabase key in config files with your project's anon key.

### No Data Displayed

**Check database connection**:
- Verify Supabase project URL
- Confirm table names match schema
- Check RLS (Row Level Security) policies

**Check data existence**:
- SMS: Send a test message first
- CRM: Verify data was imported successfully

### GUI Doesn't Show

**Windows**: Ensure `pythonw.exe` is available (comes with Python).

If `pythonw` fails, use regular `python`:
```powershell
python SMSconductor_DB.py
```

---

## 📊 Data Sources

### SMS Database (`messages` table)
- Populated by: `conductor_system.py` (incoming SMS)
- Populated by: n8n workflows (outgoing SMS from AI)
- Updated by: SMS Conductor DB Viewer (manual edits)

### CRM Database (5 tables)
- Populated by: CSV import scripts in `mota-crm/import_tools/`
- Source files:
  - `MEMBER_PERFORMANCE.csv` → `customers`
  - `total_sales_ONLY.csv` → `transactions`
  - `total_sales_products.csv` → `transaction_items`
  - `total_product_stock.csv` → `products`
  - `budtenders_only.csv` → `staff`

---

## 📈 Performance Notes

### SMS Conductor DB Viewer
- **Load time**: < 1 second (< 100 messages)
- **Refresh**: Real-time (on-demand)
- **Memory**: Minimal (~20 MB)

### CRM Integrated Viewer
- **Initial load**: 2-3 seconds (3,186 customers)
- **Transaction load**: On-demand per customer (< 1 second)
- **Item load**: On-demand per transaction (< 1 second)
- **Memory**: ~50 MB (with cached data)

### Individual Viewers
- **Customer Viewer**: 2-3 seconds (3,186 records)
- **Inventory Viewer**: 3-5 seconds (3,299 records, random sampling)
- **Transaction Viewer**: 3-5 seconds (first 1,000 records, pagination available)

---

## 🔐 Security

- ✅ All viewers read-only by default (except SMS viewer)
- ✅ Supabase credentials stored locally (git-ignored)
- ✅ Phone numbers can be masked in logs
- ⚠️ SMS viewer allows editing/deleting - use with caution
- ⚠️ No authentication - anyone with access to the batch file can launch viewers

---

**🎉 All viewers are production-ready and tested!**

