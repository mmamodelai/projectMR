# MoTa CRM - Customer Relationship Management System
**Version**: 2.0  
**Status**: Production  
**Last Updated**: October 11, 2025

---

## 🎯 Overview

**MoTa CRM** is a complete customer relationship management system with desktop GUI viewers for managing customer data, transactions, inventory, and purchase history stored in Supabase.

### Key Features:
- ✅ **Integrated CRM Viewer** - Customers, transactions, and items in one interface
- ✅ **Sortable & Editable** - Click to sort, right-click to edit
- ✅ **Product Intelligence** - View detailed product info for purchases
- ✅ **On-Demand Loading** - Efficient data fetching (no performance issues)
- ✅ **Import Tools** - CSV → Supabase for bulk data imports
- ✅ **100% Data Completeness** - 114,136 transaction items, fully imported

---

## 📊 Database Stats

**Current Data** (as of October 11, 2025):
- **Customers**: 3,186
- **Transactions**: 186,394
- **Products**: 3,299
- **Transaction Items**: 114,136 (100% complete)
- **Staff**: 50 budtenders

---

## 🚀 Quick Start

### 1. Configure Supabase

Create `config/.env`:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
```

**Don't commit this file!** (Already in `.gitignore`)

### 2. Launch CRM Viewer

**Option A: Batch File** (recommended)
```powershell
cd viewers
.\start_crm_integrated.bat
```

**Option B: Python Directly**
```powershell
cd viewers
pythonw crm_integrated.py
```

### 3. Launch All Viewers

```powershell
cd viewers
.\start_all_viewers.bat
```

This launches:
- ✅ CRM Integrated Viewer (customers + transactions + items + products)
- ✅ Inventory Viewer (all products)
- ✅ Transaction Viewer (all transactions)

---

## 🖥️ Viewers

### 1. Integrated CRM Viewer (`crm_integrated.py`)

**The main enterprise viewer** - 4-column layout with linked data.

**Features**:
- 📋 **Customer List** (left) - All 3,186 customers
  - Sortable columns (click header to sort)
  - Right-click to edit name, phone, VIP status
  - Search by name or phone
- 💰 **Transactions** (top-right) - Selected customer's purchases
  - Auto-loads when customer selected
  - Shows date, total, store
- 📦 **Items** (middle-right) - Selected transaction's line items
  - Auto-loads when transaction selected
  - Shows product, quantity, price
- 🌿 **Product Details** (bottom-right) - Selected item's full info
  - Auto-loads when item selected
  - Shows THC/CBD, strain, effects, pricing, vendor, stock

**Usage**:
1. Search/select a customer (e.g., "Aaron Campos")
2. Click a transaction → see items purchased
3. Click an item → see full product details
4. Right-click customer → edit fields

**Shortcuts**:
- Double-click customer → view full profile
- Right-click customer → edit menu

---

### 2. Inventory Viewer (`inventory_viewer_fixed.py`)

**View all products** - Full inventory management.

**Features**:
- 📦 All 3,299 products
- 🎲 "Random 1K" button - load random 1,000 products sample
- 📊 "Load All" button - load entire inventory
- Sortable columns
- Search/filter products

**Usage**:
```powershell
cd viewers
.\start_inventory_viewer.bat
```

---

### 3. Transaction Viewer (`transaction_viewer_enhanced.py`)

**View all transactions** - Purchase history across all customers.

**Features**:
- 💰 All 186,394 transactions
- Date, customer, total, store
- Sortable and searchable
- Loads first 1,000, then pagination

**Usage**:
```powershell
cd viewers
.\start_transaction_viewer.bat
```

---

## 📥 Import Tools

### Import Customers

```powershell
cd import_tools
python import_customers_to_supabase.py
```

**Input**: `MEMBER_PERFORMANCE.csv`  
**Output**: Supabase `customers` table

**Features**:
- Email cleaning/normalization
- Phone number formatting (E.164)
- VIP status calculation
- Duplicate detection

---

### Import Products

```powershell
python import_products_from_csv.py
```

**Input**: `PRODUCT_BATCH_EXPORT.csv`  
**Output**: Supabase `products` table

**Features**:
- THC/CBD content parsing
- Strain type detection
- Stock status tracking
- Vendor information

---

### Import Transactions

```powershell
python import_all_transactions.py
```

**Input**: `total_sales_products.csv`  
**Output**: Supabase `transactions` and `transaction_items` tables

**Features**:
- Transaction aggregation
- Line item parsing
- Customer/product linking
- Date normalization

**Note**: This is the most complex import (93K rows → 186K transactions + 114K items).

---

## 📁 File Structure

```
mota-crm/
├── viewers/
│   ├── crm_integrated.py              # Main CRM viewer ⭐
│   ├── inventory_viewer_fixed.py      # Product viewer
│   ├── transaction_viewer_enhanced.py # Transaction viewer
│   ├── supabase_helpers.py            # Pagination helper
│   ├── db_viewer.py                   # SMS messages viewer
│   ├── start_crm_integrated.bat       # Launch CRM
│   ├── start_inventory_viewer.bat     # Launch inventory
│   ├── start_transaction_viewer.bat   # Launch transactions
│   └── start_all_viewers.bat          # Launch all 3
│
├── import_tools/
│   ├── import_customers_to_supabase.py       # Customer import
│   ├── import_products_from_csv.py           # Product import
│   ├── import_all_transactions.py            # Transaction import
│   ├── import_transaction_items_FIXED.py     # Line items import
│   ├── import_customers.bat                  # Batch launcher
│   └── import_transactions.bat               # Batch launcher
│
├── docs/
│   ├── README_DB.md                   # Database schema details
│   ├── SUPABASE_SCHEMA_DESIGN.md      # Table design
│   ├── SYSTEM_STATUS.md               # Data completeness
│   ├── DATA_FIX_SUMMARY.md            # Data quality fixes
│   └── *.sql                          # SQL migrations/functions
│
├── config/
│   └── .env.example                   # Supabase credentials template
│
└── README.md                          # This file
```

---

## 🗄️ Database Schema

### Tables

#### `customers`
```sql
- id (uuid, primary key)
- name (text)
- email (text)
- phone_number (text)
- vip_status (boolean)
- total_visits (integer)
- lifetime_value (numeric)
- last_visit_date (date)
- average_transaction (numeric)
- created_at (timestamp)
```

#### `transactions`
```sql
- id (uuid, primary key)
- customer_id (uuid, foreign key → customers)
- date (date)
- total_amount (numeric)
- store_name (text)
- created_at (timestamp)
```

#### `transaction_items`
```sql
- id (uuid, primary key)
- transaction_id (uuid, foreign key → transactions)
- product_sku (text, foreign key → products)
- quantity (integer)
- unit_price (numeric)
```

#### `products`
```sql
- sku (text, primary key)
- name (text)
- category (text)
- thc_content (numeric)
- cbd_content (numeric)
- strain_type (text)
- effects (text)
- retail_price (numeric)
- cost (numeric)
- vendor (text)
- stock_quantity (integer)
- stock_status (text)
```

#### `staff`
```sql
- id (uuid, primary key)
- name (text)
- email (text)
- role (text)
- store (text)
```

---

## 🔍 Advanced Features

### Sortable Columns

Click any column header in the CRM viewer to sort:
- **Name** → Alphabetical A-Z / Z-A
- **Total Visits** → Most/least visits
- **Lifetime Value** → Highest/lowest spenders
- **VIP Status** → VIP customers first

### Right-Click Editing

Right-click any customer in the CRM viewer:
- **Edit Name** → Update customer name
- **Edit Phone** → Update phone number
- **Edit VIP Status** → Toggle VIP status
- **View Full Profile** → See all customer details

Changes save immediately to Supabase!

### On-Demand Data Loading

**Efficient design**:
- ✅ Customer list loads once at startup (3,186 records)
- ✅ Transactions load only when customer selected
- ✅ Items load only when transaction selected
- ✅ Product details load only when item selected

**Result**: Fast, responsive, no lag even with 186K transactions!

---

## 🐛 Troubleshooting

### Issue: Viewers won't launch

**Check Python**:
```powershell
python --version  # Should be 3.9+
```

**Install dependencies**:
```powershell
pip install supabase tkinter
```

---

### Issue: "No data loading"

**Check `.env` file**:
```powershell
Get-Content config\.env
```

Ensure `SUPABASE_URL` and `SUPABASE_KEY` are correct.

**Test Supabase connection**:
```python
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv('config/.env')
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
print(supabase.table('customers').select('id').limit(1).execute())
```

---

### Issue: "UnicodeEncodeError" on Windows

**Force UTF-8 encoding**:
```python
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
```

Already implemented in all viewers.

---

## 🧪 Testing

### Test CRM Viewer

1. Launch viewer
2. Search for "Aaron"
3. Select "Aaron Campos"
4. Click a transaction
5. Click an item
6. Right-click Aaron → Edit Name

**Expected**: All data loads correctly, edits save to Supabase.

---

### Test Import

1. Place CSV file in `import_tools/`
2. Run import script
3. Check Supabase table
4. Launch viewer to verify

**Expected**: Data appears correctly in viewer.

---

## 📈 Performance

**Typical Performance**:
- **Customer list**: ~2 seconds to load 3,186 customers
- **Transactions**: ~1 second per customer (10-50 transactions)
- **Items**: <1 second per transaction (1-10 items)
- **Product details**: <1 second per item
- **Search**: <1 second for any query
- **Edit/Save**: <2 seconds to update Supabase

**Optimizations**:
- On-demand loading (only fetch what's needed)
- Pagination helper (batch fetching)
- Indexed searches (Supabase indexes)
- Local caching (customer list cached)

---

## 🔗 Integration

### With Conductor SMS

- View SMS messages in `db_viewer.py`
- Link SMS to customers by phone number
- Track customer communication history

### With MotaBot AI

- MotaBot queries CRM for customer data
- Uses customer name, VIP status, visits, lifetime value
- Personalizes AI responses based on CRM data

---

## 🆘 Support

**View detailed database documentation**:
```
docs/README_DB.md
```

**Check system status**:
```
docs/SYSTEM_STATUS.md
```

**GitHub**: https://github.com/mmamodelai/ConductorV4.1/issues

---

## 📜 Version History

### v2.0 - October 11, 2025
- Integrated CRM viewer with 4-column layout
- Sortable columns (click to sort)
- Right-click editing
- Product intelligence panel
- On-demand data loading
- Fixed transaction items import (100% complete)
- Removed CSV files from repo (already imported)

### v1.0 - September 2025
- Initial CRM viewers
- CSV import tools
- Supabase integration

---

**🎉 MoTa CRM is production-ready! Full-featured customer relationship management with powerful desktop viewers.**
