# Supabase Databases Overview
**Last Updated**: October 12, 2025  
**Project**: Conductor V4.1

---

## 🗄️ Database Architecture

The Conductor V4.1 system uses **ONE Supabase project** with **SIX tables** split across two logical databases:

```
Supabase Project: https://kiwmwoqrguyrcpjytgte.supabase.co
├── SMS Database (1 table)
│   └── messages
└── CRM Database (5 tables)
    ├── customers
    ├── transactions
    ├── transaction_items
    ├── products
    └── staff
```

---

## 📱 SMS Database

**Purpose**: Store all SMS messages (inbound/outbound) for the Conductor SMS system

### Table: `messages`

**Current Records**: 11 messages

| Column | Type | Description |
|--------|------|-------------|
| `id` | bigint | Primary key (auto-increment) |
| `phone_number` | text | E.164 format (+1234567890) |
| `content` | text | SMS message body |
| `timestamp` | timestamptz | When message was created |
| `modem_timestamp` | timestamptz | When modem received/sent |
| `status` | text | `sent`, `queued`, `failed`, `unread`, `read` |
| `direction` | text | `inbound` or `outbound` |
| `modem_index` | int | Modem storage index |
| `message_hash` | text | Duplicate detection hash |
| `retry_count` | int | Number of send attempts |
| `last_retry_at` | timestamptz | Last retry timestamp |
| `created_at` | timestamptz | Database creation time |
| `updated_at` | timestamptz | Last update time |

**Current Breakdown**:
- ✅ **Sent**: 3 messages
- 📖 **Read**: 8 messages
- 📥 **Inbound**: 8 messages
- 📤 **Outbound**: 3 messages

**Used By**:
- `conductor_system.py` - Reads/writes messages
- `SMSconductor_DB.py` - GUI viewer for messages
- MotaBot AI n8n workflow - Reads unread messages, writes AI responses

**Credentials Location**: `conductor-sms/config.json`

---

## 🏢 CRM Database

**Purpose**: Store customer data, transactions, and inventory for MoTa dispensary

### Table: `customers`

**Current Records**: 3,186 customers

| Column | Type | Description |
|--------|------|-------------|
| `id` | uuid | Primary key |
| `name` | text | Customer full name |
| `email` | text | Email address |
| `phone` | text | Phone number (E.164) |
| `visit_count` | int | Total visits |
| `lifetime_value` | numeric | Total spend ($) |
| `first_visit_date` | date | First purchase date |
| `last_visit_date` | date | Most recent purchase |
| `vip_status` | text | `New`, `Casual`, `Regular`, `VIP` |
| `churn_risk` | text | `Low`, `Medium`, `High` |
| `avg_transaction_value` | numeric | Average purchase ($) |
| `days_since_last_visit` | int | Recency metric |
| `preferred_location` | text | Most visited store |
| `preferred_budtender` | text | Favorite staff member |
| `created_at` | timestamptz | Record creation |
| `updated_at` | timestamptz | Last update |

**VIP Status Logic** (auto-calculated by triggers):
- **VIP**: 16+ visits
- **Regular**: 6-15 visits
- **Casual**: 2-5 visits
- **New**: 1 visit

**Churn Risk Logic**:
- **High**: 60+ days since last visit
- **Medium**: 30-59 days
- **Low**: < 30 days

---

### Table: `transactions`

**Current Records**: 186,394 transactions

| Column | Type | Description |
|--------|------|-------------|
| `id` | uuid | Primary key |
| `transaction_id` | int | Transaction number |
| `customer_id` | uuid | Foreign key → customers |
| `date` | date | Transaction date |
| `total` | numeric | Total amount ($) |
| `payment_method` | text | Payment type |
| `location` | text | Store location |
| `staff_id` | uuid | Foreign key → staff |
| `created_at` | timestamptz | Record creation |

**Total Revenue**: ~$2.16M tracked

---

### Table: `transaction_items`

**Current Records**: 114,136 line items (100% complete)

| Column | Type | Description |
|--------|------|-------------|
| `id` | uuid | Primary key |
| `transaction_id` | int | Foreign key → transactions |
| `product_sku` | text | Foreign key → products |
| `quantity` | int | Units purchased |
| `unit_price` | numeric | Price per unit ($) |
| `total_price` | numeric | Line item total ($) |
| `discount` | numeric | Discount applied ($) |
| `created_at` | timestamptz | Record creation |

**Data Integrity**: ✅ All items properly linked to transactions (fixed Oct 11, 2025)

---

### Table: `products`

**Current Records**: 3,299 products

| Column | Type | Description |
|--------|------|-------------|
| `id` | uuid | Primary key |
| `sku` | text | Product SKU (unique) |
| `name` | text | Product name |
| `category` | text | Product category |
| `brand` | text | Manufacturer |
| `thc_content` | text | THC percentage/mg |
| `cbd_content` | text | CBD percentage/mg |
| `strain_type` | text | Indica, Sativa, Hybrid |
| `effects` | text | Expected effects |
| `unit_cost` | numeric | Wholesale cost ($) |
| `retail_price` | numeric | Retail price ($) |
| `current_stock` | int | Units in stock |
| `stock_status` | text | In stock, Low, Out of stock |
| `vendor` | text | Supplier name |
| `last_restocked` | date | Last restock date |
| `created_at` | timestamptz | Record creation |
| `updated_at` | timestamptz | Last update |

---

### Table: `staff`

**Current Records**: Unknown (estimated ~50 budtenders)

| Column | Type | Description |
|--------|------|-------------|
| `id` | uuid | Primary key |
| `name` | text | Staff full name |
| `employee_id` | text | Employee number |
| `role` | text | Position title |
| `location` | text | Primary store |
| `hire_date` | date | Date hired |
| `active` | boolean | Currently employed |
| `created_at` | timestamptz | Record creation |

---

## 🔗 Table Relationships

```
customers (3,186)
    ↓
transactions (186,394)  ← staff (50)
    ↓
transaction_items (114,136)
    ↓
products (3,299)
```

**Example Query Path**:
1. Customer "John Doe" (customer_id: abc-123)
2. → Has transactions (transaction IDs: 550995, 551000, etc.)
3. → Each transaction has items (product SKU: "FLOWER-123", quantity: 2)
4. → Each item links to product details (name, THC, price, etc.)

---

## 🔐 Credentials

### SMS Database
**Location**: `conductor-sms/config.json`
```json
{
  "database": {
    "use_supabase": true,
    "supabase_url": "https://kiwmwoqrguyrcpjytgte.supabase.co",
    "supabase_key": "eyJhbGci..."
  }
}
```

### CRM Database
**Location**: Hardcoded in Python files
- `mota-crm/viewers/crm_integrated.py` (line 14-15)
- `mota-crm/viewers/inventory_viewer_fixed.py`
- `mota-crm/viewers/transaction_viewer_enhanced.py`
- `mota-crm/import_tools/*.py`

**Same Project**: Both SMS and CRM use the same Supabase project, just different tables.

---

## 📊 Storage Usage

| Database | Tables | Records | Estimated Size |
|----------|--------|---------|----------------|
| **SMS** | 1 | 11 | < 1 MB |
| **CRM** | 5 | 307,013 | ~50-100 MB |
| **Total** | 6 | 307,024 | ~50-100 MB |

**Supabase Free Tier**: 500 MB database size (well within limits)

---

## 🚫 What's NOT Used

### Local SQLite Database
**Location**: `conductor-sms/database/olive_sms.db`  
**Size**: 68 KB  
**Records**: 151 messages (stale data from Oct 7)  
**Status**: ❌ **NOT USED** - System configured to use Supabase

**Why it exists**:
- Legacy fallback for when `use_supabase` is `false` in `config.json`
- Useful if Supabase is ever down
- Code still supports it (good for redundancy)

**Recommendation**: 
- ✅ Keep the code that supports SQLite (good fallback)
- ❌ Delete the actual `olive_sms.db` file (it's stale/unused)
- ✅ Keep the `database/` directory (code expects it)

---

## 🔄 Data Flow

### Inbound SMS
```
Modem → conductor_system.py → Supabase (messages table) 
                                    ↓
                              n8n MotaBot reads
                                    ↓
                              AI generates response
                                    ↓
                              Supabase (queued) → conductor_system.py → Modem
```

### CRM Lookups
```
SMS arrives with phone number (+16193683370)
    ↓
MotaBot queries Supabase (customers table) by phone
    ↓
Retrieves: name, VIP status, visits, lifetime value
    ↓
AI uses this data for personalized response
```

---

## 🛠️ Management Tools

### SMS Database
- **GUI Viewer**: `conductor-sms/start_SMSconductor_DB.bat`
- **CLI Status**: `python conductor_system.py status`

### CRM Database
- **Integrated Viewer**: `mota-crm/viewers/start_crm_integrated.bat`
- **Individual Viewers**: `mota-crm/viewers/start_all_viewers.bat`
- **Import Tools**: `mota-crm/import_tools/*.py`

---

## 📈 Growth Projections

| Metric | Current | 1 Year Projection |
|--------|---------|-------------------|
| **SMS Messages** | 11 | ~50,000 (daily messages) |
| **Customers** | 3,186 | ~5,000 (new signups) |
| **Transactions** | 186,394 | ~400,000 (daily sales) |
| **Products** | 3,299 | ~5,000 (new inventory) |

**Database Size Estimate**: 500 MB in 1 year (still within free tier with cleanup)

---

## 🔒 Security Notes

- ✅ Supabase credentials are in local config files (git-ignored)
- ✅ RLS (Row Level Security) policies should be reviewed
- ✅ Anon key is used (read/write access)
- ⚠️ Consider using service role key for server-side operations
- ⚠️ No authentication on GUI viewers (anyone with file access can view)

---

## 📝 Summary

**Total Supabase Setup**:
- **1 Project**: `kiwmwoqrguyrcpjytgte.supabase.co`
- **6 Tables**: 1 SMS + 5 CRM
- **307,024 Total Records**
- **~50-100 MB Storage**
- **2 Databases** (logical separation):
  - SMS Conductor (messages)
  - MoTa CRM (customers, transactions, items, products, staff)

**Local SQLite**: NOT USED (can be deleted)

---

**For detailed table schemas, see `mota-crm/docs/README_DB.md`**

