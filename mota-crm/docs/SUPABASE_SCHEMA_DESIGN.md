# Supabase Database Schema for MoTa CRM System

**Version**: 2.0 Ultimate  
**Last Updated**: October 11, 2025  
**Status**: Production - Fully Deployed + Product Intelligence Integration

---

## 🎯 System Overview

### What We Have Now
```
┌─────────────────────────────────────────────────────────────────┐
│                    MOTA CRM - ULTIMATE SYSTEM                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  CUSTOMERS (10,047)  →  TRANSACTIONS (36,463)                  │
│       ↓                       ↓                                 │
│  Customer Profile      Transaction Items (57,568)               │
│  • Name, Phone              ↓                                   │
│  • Points, Visits     PRODUCTS (39,555 + 1,690 inventory)      │
│  • VIP Status         • Cannabis Profile (THC/CBD)             │
│  • Churn Risk         • Pricing & Cost                         │
│  • Lifetime Value     • Stock Levels                           │
│                       • Vendor Info                            │
│                       • Age of Stock                           │
│                       • Usage Suggestions                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 Database Tables (Current)

### 1. `customers` - Customer Intelligence
**Rows**: 10,047 customers  
**Purpose**: Core customer data for AI personalization

```sql
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    member_id TEXT UNIQUE NOT NULL,
    name TEXT,
    phone TEXT,
    email TEXT,
    
    -- Loyalty Data
    loyalty_points DECIMAL(10, 2) DEFAULT 0,
    total_visits INTEGER DEFAULT 0,
    total_sales INTEGER DEFAULT 0,
    total_refunds INTEGER DEFAULT 0,
    
    -- Financial Data
    gross_sales DECIMAL(10, 2) DEFAULT 0,
    gross_refunds DECIMAL(10, 2) DEFAULT 0,
    avg_sale_value DECIMAL(10, 2) DEFAULT 0,
    lifetime_value DECIMAL(10, 2) DEFAULT 0,
    
    -- Customer Profile
    customer_type TEXT,
    member_group TEXT,
    marketing_source TEXT,
    state TEXT,
    zip_code TEXT,
    
    -- Dates
    date_joined DATE,
    last_visited DATE,
    
    -- Calculated Segmentation
    vip_status TEXT,  -- VIP, Regular, Casual, New
    churn_risk TEXT,  -- High, Medium, Low
    days_since_last_visit INTEGER,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for fast lookups
CREATE INDEX idx_customers_phone ON customers(phone);
CREATE INDEX idx_customers_member_id ON customers(member_id);
CREATE INDEX idx_customers_vip_status ON customers(vip_status);
```

**Key Features**:
- ✅ Instant phone number lookup
- ✅ Automatic VIP status calculation
- ✅ Churn risk scoring
- ✅ Lifetime value tracking

---

### 2. `transactions` - Purchase History
**Rows**: 36,463 transactions  
**Purpose**: Track every purchase, link customers to products

```sql
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    transaction_id TEXT UNIQUE NOT NULL,
    customer_id TEXT REFERENCES customers(member_id),
    
    -- Transaction Details
    date TIMESTAMPTZ,
    total_amount DECIMAL(10, 2),
    gross_sales DECIMAL(10, 2),
    net_sales DECIMAL(10, 2),
    
    -- Store Info
    staff_name TEXT,
    location TEXT,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_transactions_customer ON transactions(customer_id);
CREATE INDEX idx_transactions_date ON transactions(date);
```

**Key Features**:
- ✅ Links customers to their purchase history
- ✅ Date-based analysis
- ✅ Staff performance tracking

---

### 3. `transaction_items` - Individual Items Purchased
**Rows**: 57,568 line items  
**Purpose**: What exact products did customers buy

```sql
CREATE TABLE transaction_items (
    id SERIAL PRIMARY KEY,
    transaction_id TEXT REFERENCES transactions(transaction_id),
    product_id TEXT,
    
    -- Item Details
    product_name TEXT,
    brand TEXT,
    category TEXT,
    quantity INTEGER DEFAULT 1,
    total_price DECIMAL(10, 2),
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_items_transaction ON transaction_items(transaction_id);
CREATE INDEX idx_items_product ON transaction_items(product_id);
```

**Key Features**:
- ✅ See exactly what customers bought
- ✅ Product preference analysis
- ✅ Repurchase tracking

---

### 4. `products` - Product Intelligence (CURRENT + NEW DATA)
**Current Rows**: 39,555 products (from sales data)  
**New Data**: 1,690 inventory items with FULL intelligence  
**Purpose**: Complete product information + inventory management

#### **Current Schema**:
```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    product_id TEXT UNIQUE,
    name TEXT,
    brand TEXT,
    category TEXT,
    
    -- Cannabis Profile (CURRENT)
    flower_type TEXT,  -- Sativa, Indica, Hybrid
    strain TEXT,
    thc_content DECIMAL(5, 2),
    cbd_content DECIMAL(5, 2),
    
    -- Pricing (CURRENT)
    retail_price DECIMAL(10, 2),
    cost DECIMAL(10, 2),  -- Currently NULL
    
    -- Basic Info (CURRENT)
    sku TEXT,
    vendor TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### **PROPOSED SCHEMA (Product Intelligence v2.0)**:
```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    product_id TEXT UNIQUE NOT NULL,
    sku TEXT,
    
    -- Product Identity
    name TEXT NOT NULL,
    brand TEXT,
    category TEXT,  -- Flower, Vapes, Edibles, Concentrates, etc.
    
    -- Cannabis Profile
    flower_type TEXT,  -- Sativa, Indica, Hybrid
    strain TEXT,
    thc_percent DECIMAL(5, 2),  -- THC percentage
    cbd_percent DECIMAL(5, 2),  -- CBD percentage
    thc_mg DECIMAL(10, 2),      -- THC in milligrams
    cbd_mg DECIMAL(10, 2),      -- CBD in milligrams
    
    -- Pricing & Cost Analysis
    retail_price DECIMAL(10, 2),
    cost_per_unit DECIMAL(10, 2),      -- NEW: What you paid
    purchased_cost DECIMAL(10, 2),     -- NEW: Total purchase cost
    profit_margin DECIMAL(5, 2),       -- NEW: Calculated (retail - cost) / retail
    
    -- Inventory Management
    current_stock INTEGER DEFAULT 0,    -- NEW: Quantity on hand
    purchased_qty INTEGER,              -- NEW: Original purchase quantity
    status TEXT,                        -- NEW: Active, Inactive, Archived
    is_archived BOOLEAN DEFAULT FALSE,  -- NEW: Archived flag
    is_in_stock BOOLEAN,                -- NEW: Calculated: current_stock > 0
    is_low_stock BOOLEAN,               -- NEW: Calculated: current_stock < 5
    
    -- Vendor & Supply Chain
    vendor_name TEXT,                   -- NEW: Supplier name
    
    -- Date Intelligence
    purchased_date DATE,                -- NEW: When you bought it
    received_date DATE,                 -- NEW: When you received it
    expiration_date DATE,               -- NEW: When it expires
    age_in_stock INTEGER,               -- NEW: Calculated: days since purchased
    days_until_expiration INTEGER,      -- NEW: Calculated: days until exp
    is_expiring_soon BOOLEAN,           -- NEW: Calculated: < 30 days to exp
    
    -- Product Description & Effects
    effects_description TEXT,           -- NEW: Auto-generated based on type
    usage_suggestion TEXT,              -- NEW: Auto-generated based on category
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_products_sku ON products(sku);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_brand ON products(brand);
CREATE INDEX idx_products_stock ON products(current_stock);
CREATE INDEX idx_products_status ON products(status);
CREATE INDEX idx_products_vendor ON products(vendor_name);
```

#### **New Columns Explained**:

**Cost Analysis**:
- `cost_per_unit`: What you paid per unit
- `purchased_cost`: Total cost of purchase
- `profit_margin`: Automatically calculated percentage

**Inventory**:
- `current_stock`: Real-time quantity (from PRODUCT_BATCH_EXPORT.csv)
- `purchased_qty`: Original order quantity
- `status`: Active/Inactive/Archived
- `is_in_stock`: Auto-calculated boolean
- `is_low_stock`: Auto-calculated alert flag

**Supply Chain**:
- `vendor_name`: Who supplies it
- `purchased_date`: When you ordered it
- `received_date`: When it arrived
- `expiration_date`: When it expires

**Intelligence**:
- `age_in_stock`: Days since purchased (auto-calculated)
- `days_until_expiration`: Days until expiration (auto-calculated)
- `is_expiring_soon`: Alert if < 30 days (auto-calculated)

**AI Enhancement**:
- `effects_description`: "High Energy • Uplifting • Creative • Daytime"
- `usage_suggestion`: "Best for: Morning/Daytime, Activities"

---

### 5. `staff` - Employee Information
**Rows**: ~50-100 budtenders  
**Purpose**: Track staff performance, customer preferences

```sql
CREATE TABLE staff (
    id SERIAL PRIMARY KEY,
    staff_name TEXT UNIQUE NOT NULL,
    
    -- Performance Metrics
    total_sales DECIMAL(10, 2) DEFAULT 0,
    total_transactions INTEGER DEFAULT 0,
    avg_transaction_value DECIMAL(10, 2),
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 🔥 Database Views (Aggregated Intelligence)

### `customer_purchase_history`
Combines customers + transactions + items for full purchase analysis

```sql
CREATE VIEW customer_purchase_history AS
SELECT 
    c.member_id,
    c.name,
    c.phone,
    t.transaction_id,
    t.date,
    t.total_amount,
    ti.product_name,
    ti.brand,
    ti.category,
    ti.quantity,
    ti.total_price
FROM customers c
JOIN transactions t ON c.member_id = t.customer_id
JOIN transaction_items ti ON t.transaction_id = ti.transaction_id;
```

### `customer_spending_analysis`
Financial analysis per customer

```sql
CREATE VIEW customer_spending_analysis AS
SELECT 
    c.member_id,
    c.name,
    c.phone,
    COUNT(DISTINCT t.transaction_id) as total_transactions,
    SUM(t.total_amount) as lifetime_spend,
    AVG(t.total_amount) as avg_transaction,
    MAX(t.date) as last_purchase_date,
    EXTRACT(DAY FROM NOW() - MAX(t.date)) as days_since_last_purchase
FROM customers c
LEFT JOIN transactions t ON c.member_id = t.customer_id
GROUP BY c.member_id, c.name, c.phone;
```

---

## 📁 File Organization Structure

```
mota finance/
├── README.md                              # Main overview
├── README_DB.md                           # Database usage guide
├── SUPABASE_SCHEMA_DESIGN.md             # This file - schema documentation
├── ULTIMATE_CRM_GUIDE.md                  # CRM viewer guide
├── VIEWERS_GUIDE.md                       # All viewer documentation
│
├── DATA FILES (Source CSVs)
│   ├── MEMBER_PERFORMANCE.csv             # Customer data (10,047)
│   ├── total_sales_products.csv           # Transaction data (36,463)
│   ├── PRODUCT_BATCH_EXPORT.csv           # Inventory data (1,690)
│   └── SELL_THROUGH_REPORT.csv            # Product performance
│
├── MIGRATION SCRIPTS (SQL)
│   ├── create_customers_table.sql         # Customer table schema
│   ├── create_transaction_tables.sql      # Transaction/items/products/staff
│   └── create_product_intelligence.sql    # NEW: Product v2.0 schema
│
├── IMPORT SCRIPTS (Python)
│   ├── import_customers_to_supabase.py    # Import customers
│   ├── import_all_transactions.py         # Import transactions
│   ├── import_transaction_items.py        # Import line items
│   ├── import_products_from_csv.py        # Import products (basic)
│   └── import_product_intelligence.py     # NEW: Import full inventory
│
├── VIEWER APPLICATIONS (Tkinter GUIs)
│   ├── crm_ultimate.py                    # 4-column ultimate viewer
│   ├── crm_integrated.py                  # 3-column integrated viewer
│   ├── crm_viewer_unlimited.py            # Customer-only viewer
│   ├── inventory_viewer_fixed.py          # Product inventory viewer
│   └── transaction_viewer_enhanced.py     # Transaction viewer
│
├── BATCH FILES (Windows launchers)
│   ├── start_crm_ultimate.bat             # Launch ultimate CRM
│   ├── start_crm_integrated.bat           # Launch integrated CRM
│   ├── start_all_viewers.bat              # Launch all viewers
│   ├── import_customers.bat               # Import customer data
│   └── import_product_intelligence.bat    # NEW: Import inventory
│
└── HELPER MODULES
    ├── supabase_helpers.py                # Pagination helper
    └── check_available_data.py            # Data availability checker
```

---

## 🚀 Data Pipeline

### Current State (✅ Completed):
1. **Customer Data**: 10,047 customers imported from MEMBER_PERFORMANCE.csv
2. **Transaction Data**: 36,463 transactions imported from total_sales_products.csv
3. **Transaction Items**: 57,568 line items imported
4. **Basic Products**: 39,555 products from sales data
5. **Staff**: ~50 budtenders imported

### Next Step (🔄 In Progress):
6. **Product Intelligence**: Import 1,690 inventory items from PRODUCT_BATCH_EXPORT.csv
   - Stock levels
   - Cost data
   - Vendor information
   - Purchase/expiration dates
   - Calculate age in stock
   - Calculate profit margins

---

## 🎯 Ultimate CRM Capabilities

### When User Clicks on a Product, They See:

#### **PRODUCT PROFILE**
- Name, SKU, Brand
- Category (Flower, Vapes, Edibles, etc.)

#### **CANNABIS INTELLIGENCE**
- THC: 25.3%
- CBD: 0.8%
- Type: Sativa / Indica / Hybrid
- Strain: Blue Dream, OG Kush, etc.
- Effects: "High Energy • Uplifting • Creative • Daytime Use"

#### **BUSINESS INTELLIGENCE**
- Retail Price: $40.00
- Cost: $25.00
- Margin: 37.5%
- Vendor: MOTA Distribution

#### **INVENTORY STATUS**
- Current Stock: 47 units
- Status: IN STOCK
- Age in Stock: 23 days
- Purchased: 2025-09-18
- Expires: 2026-01-15 (95 days)

#### **USAGE SUGGESTIONS**
- Best for: Morning/Daytime, Activities, Social Events
- Effects: High Energy, Uplifting, Creative
- Recommended for: New customers, Sativa lovers

---

## 📊 Performance Metrics

### Current Database Size:
- **Customers**: 10,047 rows (~2 MB)
- **Transactions**: 36,463 rows (~5 MB)
- **Transaction Items**: 57,568 rows (~8 MB)
- **Products**: 39,555 rows (~15 MB)
- **Total**: ~30 MB in database

### After Product Intelligence Import:
- **Products**: 39,555 + 1,690 = 41,245 rows (~18 MB)
- **Total**: ~33 MB in database

### Query Performance:
- Phone lookup: < 50ms
- Transaction history: < 100ms
- Product details: < 50ms
- All data for 1 customer: < 200ms

---

## 🔄 Automated Calculations

### Products Table Triggers:

#### **Calculate Profit Margin**:
```sql
CREATE OR REPLACE FUNCTION calculate_profit_margin()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.retail_price > 0 AND NEW.cost_per_unit IS NOT NULL THEN
        NEW.profit_margin := ((NEW.retail_price - NEW.cost_per_unit) / NEW.retail_price) * 100;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_calculate_profit_margin
BEFORE INSERT OR UPDATE ON products
FOR EACH ROW
EXECUTE FUNCTION calculate_profit_margin();
```

#### **Calculate Stock Status**:
```sql
CREATE OR REPLACE FUNCTION calculate_stock_status()
RETURNS TRIGGER AS $$
BEGIN
    NEW.is_in_stock := (NEW.current_stock > 0);
    NEW.is_low_stock := (NEW.current_stock > 0 AND NEW.current_stock < 5);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_calculate_stock_status
BEFORE INSERT OR UPDATE ON products
FOR EACH ROW
EXECUTE FUNCTION calculate_stock_status();
```

#### **Calculate Age in Stock**:
```sql
CREATE OR REPLACE FUNCTION calculate_age_in_stock()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.purchased_date IS NOT NULL THEN
        NEW.age_in_stock := EXTRACT(DAY FROM NOW() - NEW.purchased_date);
    END IF;
    
    IF NEW.expiration_date IS NOT NULL THEN
        NEW.days_until_expiration := EXTRACT(DAY FROM NEW.expiration_date - NOW());
        NEW.is_expiring_soon := (NEW.days_until_expiration < 30);
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_calculate_age_in_stock
BEFORE INSERT OR UPDATE ON products
FOR EACH ROW
EXECUTE FUNCTION calculate_age_in_stock();
```

---

## 🎯 AI Integration Points

### What the AI Can Access:

1. **Customer Profile** (by phone number)
   - Name, points, visits, VIP status
   - Last visit date, churn risk
   - Lifetime value, average spend

2. **Purchase History** (by customer)
   - All transactions with dates
   - Every item purchased
   - Spending patterns

3. **Product Intelligence** (by product ID or name)
   - Full cannabis profile (THC/CBD)
   - Cost and margin data
   - Stock status and availability
   - Age in stock, expiration info
   - Effects and usage suggestions

4. **Staff Performance** (by staff name)
   - Total sales, transaction count
   - Average transaction value

---

## 🔐 Data Privacy & Security

### AI Safety Rules:
- ✅ AI can share customer's OWN data (name, points, visits)
- ❌ AI cannot share OTHER customers' data
- ❌ AI cannot reveal exact stock quantities to customers
- ❌ AI cannot reveal cost/margin data to customers
- ✅ AI can use stock status (in stock / out of stock)
- ✅ AI can use effects/usage suggestions

---

## 📈 Future Enhancements

### Phase 3 (Future):
- **Product Images**: Add image URLs for product photos
- **Customer Reviews**: Track ratings and reviews
- **Automated Reordering**: Alert when stock < reorder point
- **Sales Velocity**: Track how fast products sell
- **Seasonal Trends**: Analyze sales patterns by season
- **Customer Segmentation**: ML-based customer clustering
- **Predictive Restocking**: AI-powered inventory forecasting

---

**Status**: Schema v2.0 - Ready for Product Intelligence Integration  
**Last Updated**: October 11, 2025  
**Next Action**: Create migration SQL and import script for PRODUCT_BATCH_EXPORT.csv
