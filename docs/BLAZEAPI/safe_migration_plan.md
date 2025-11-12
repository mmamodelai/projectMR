# Safe Blaze API Migration Plan - Parallel Tables Approach

**Strategy**: Create mirrored tables hydrated from API, run parallel to existing, then switch when validated.

## 🚨 CRITICAL API RULES (Must Follow)

From `docs/BLAZEAPI/rules from blaze.md`:

1. **Rate Limit**: **MAX 10,000 calls per 5 minutes** (hard limit - key gets disabled if exceeded!)
2. **Members**: Fetch hourly or **nightly** (use `modified` date for incremental sync)
3. **Transactions**: Fetch hourly or **nightly** for historical data
4. **Products**: Fetch **no more than every 5 minutes**, use `modified` date
5. **Incremental Sync**: Always use `modified` date to avoid re-fetching unchanged data
6. **Cost**: Tier 1 = $100/month, 250K calls (we're in 90-day grace period)

## 📊 Phase 1: Create Mirrored Tables (Safe, No API Calls Yet)

### SQL Schema for New Tables

```sql
-- Customers from Blaze API
CREATE TABLE customers_blaze (
    id SERIAL PRIMARY KEY,
    member_id TEXT UNIQUE NOT NULL,
    
    -- Core fields (from Blaze Member)
    name TEXT,
    phone TEXT,
    email TEXT,
    state TEXT,
    zip_code TEXT,
    street_address TEXT,
    city TEXT,
    
    -- Status flags
    is_medical BOOLEAN,
    text_opt_in BOOLEAN,
    email_opt_in BOOLEAN,
    member_status TEXT, -- Active/Pending/Inactive from Blaze
    
    -- Dates
    last_visited DATE,
    date_joined DATE,
    
    -- Blaze metadata for sync
    blaze_created TIMESTAMPTZ,
    blaze_modified TIMESTAMPTZ,
    
    -- Sync tracking
    last_synced_at TIMESTAMPTZ DEFAULT NOW(),
    sync_status TEXT DEFAULT 'pending', -- pending, synced, error
    
    -- Calculated fields (computed from transactions_blaze)
    loyalty_points DECIMAL(10, 2) DEFAULT 0,
    total_visits INTEGER DEFAULT 0,
    lifetime_value DECIMAL(10, 2) DEFAULT 0,
    days_since_last_visit INTEGER,
    vip_status TEXT,
    churn_risk TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_customers_blaze_member_id ON customers_blaze(member_id);
CREATE INDEX idx_customers_blaze_modified ON customers_blaze(blaze_modified);
CREATE INDEX idx_customers_blaze_sync_status ON customers_blaze(sync_status);

-- Transactions from Blaze API
CREATE TABLE transactions_blaze (
    id SERIAL PRIMARY KEY,
    transaction_id TEXT UNIQUE NOT NULL,
    customer_id TEXT, -- member_id from Blaze
    
    -- Core transaction data
    date TIMESTAMPTZ,
    total_amount DECIMAL(10, 2),
    total_tax DECIMAL(10, 2),
    discounts DECIMAL(10, 2),
    payment_type TEXT,
    
    -- Status
    blaze_status TEXT, -- Queued/Completed/Refund/etc.
    trans_type TEXT, -- Sale/Refund/Adjustment
    
    -- Location/Staff (store IDs for now)
    shop_id TEXT,
    seller_id TEXT,
    terminal_id TEXT,
    
    -- Timestamps from Blaze
    start_time TIMESTAMPTZ,
    end_time TIMESTAMPTZ,
    completed_time TIMESTAMPTZ,
    blaze_created TIMESTAMPTZ,
    blaze_modified TIMESTAMPTZ,
    
    -- Sync tracking
    last_synced_at TIMESTAMPTZ DEFAULT NOW(),
    sync_status TEXT DEFAULT 'pending',
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_transactions_blaze_transaction_id ON transactions_blaze(transaction_id);
CREATE INDEX idx_transactions_blaze_customer_id ON transactions_blaze(customer_id);
CREATE INDEX idx_transactions_blaze_modified ON transactions_blaze(blaze_modified);
CREATE INDEX idx_transactions_blaze_date ON transactions_blaze(date);

-- Transaction Items from Blaze API
CREATE TABLE transaction_items_blaze (
    id SERIAL PRIMARY KEY,
    transaction_id TEXT NOT NULL,
    
    -- Product info
    product_id TEXT,
    product_sku TEXT,
    product_name TEXT,
    brand TEXT,
    category TEXT,
    
    -- Pricing
    quantity DECIMAL(10, 2),
    unit_price DECIMAL(10, 2),
    total_price DECIMAL(10, 2),
    discount DECIMAL(10, 2),
    tax DECIMAL(10, 2),
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_items_blaze_transaction_id ON transaction_items_blaze(transaction_id);
CREATE INDEX idx_items_blaze_product_id ON transaction_items_blaze(product_id);

-- Products from Blaze API
CREATE TABLE products_blaze (
    id SERIAL PRIMARY KEY,
    product_id TEXT UNIQUE NOT NULL,
    sku TEXT UNIQUE,
    
    -- Core product data
    name TEXT NOT NULL,
    description TEXT,
    category_id TEXT,
    vendor_id TEXT,
    
    -- Pricing
    retail_price DECIMAL(10, 2),
    unit_value DECIMAL(10, 2),
    weight_per_unit TEXT,
    
    -- Potency
    thc_content DECIMAL(5, 2),
    cbd_content DECIMAL(5, 2),
    thca DECIMAL(5, 2),
    cbda DECIMAL(5, 2),
    cbg DECIMAL(5, 2),
    
    -- Status
    is_active BOOLEAN,
    
    -- Media
    image_url TEXT,
    
    -- Blaze metadata
    blaze_created TIMESTAMPTZ,
    blaze_modified TIMESTAMPTZ,
    
    -- Sync tracking
    last_synced_at TIMESTAMPTZ DEFAULT NOW(),
    sync_status TEXT DEFAULT 'pending',
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_products_blaze_product_id ON products_blaze(product_id);
CREATE INDEX idx_products_blaze_sku ON products_blaze(sku);
CREATE INDEX idx_products_blaze_modified ON products_blaze(blaze_modified);

-- Sync state tracking
CREATE TABLE blaze_sync_state (
    id SERIAL PRIMARY KEY,
    entity_type TEXT UNIQUE NOT NULL, -- 'members', 'transactions', 'products'
    last_sync_start TIMESTAMPTZ,
    last_sync_end TIMESTAMPTZ,
    last_sync_window_start TIMESTAMPTZ, -- For incremental sync
    last_sync_window_end TIMESTAMPTZ,
    records_synced INTEGER DEFAULT 0,
    records_failed INTEGER DEFAULT 0,
    sync_status TEXT DEFAULT 'idle', -- idle, running, error, completed
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 🧪 Phase 2: TEST FIRST (Before Any Overnight Script)

### Test Script Goals

1. **Verify API access** (already done ✅)
2. **Test small batch** (10 records each)
3. **Verify field mappings** (data transforms correctly)
4. **Test rate limiting** (ensure we stay under 10K/5min)
5. **Test incremental sync** (modified date filtering)

### Safe Test Plan

```python
# Test script: blaze_api_test_small.py
"""
TEST ONLY - Fetch 10 records each, verify mappings
DO NOT RUN OVERNIGHT SCRIPT UNTIL THIS PASSES
"""

# Test 1: Members (10 records, last 24h)
# Test 2: Transactions (10 records)
# Test 3: Products (10 records)
# Test 4: Verify all fields map correctly
# Test 5: Verify rate limit (should be < 100 calls total)
```

**Success Criteria**:
- ✅ All 10 records fetch correctly
- ✅ Field mappings work (dates convert, nested objects extract)
- ✅ Data inserts into `*_blaze` tables
- ✅ No errors, no rate limit warnings
- ✅ Test completes in < 30 seconds

---

## 🌙 Phase 3: Overnight Sync Script (Conservative)

### Rate Limit Safety Calculations

**Blaze Rule**: MAX 10,000 calls per 5 minutes

**Conservative Approach**:
- **Target**: Use only 50% of limit = **5,000 calls per 5 minutes**
- **Safety buffer**: Leaves room for errors, retries, other scripts

**Call Budget Per Sync**:
- Members: ~500 calls (with pagination)
- Transactions: ~500 calls (with pagination)
- Products: ~500 calls (with pagination)
- **Total**: ~1,500 calls per sync session
- **Time**: ~8 minutes per sync (well under 5,000/5min limit)

### Incremental Sync Strategy

**Members** (Nightly):
- Fetch only records where `modified > last_sync_window_start`
- Use `startDate` and `endDate` (epoch ms)
- Batch size: 500 records per page
- Paginate with `skip` and `limit`

**Transactions** (Nightly):
- Fetch only records where `modified > last_sync_window_start`
- Use `startDate` and `endDate` (ISO timestamps)
- Batch size: 500 records per page
- **Note**: Transactions include `cart.items[]` - extract items separately

**Products** (Every 5 minutes during business hours, nightly full sync):
- Use `/api/v1/partner/products/modified?startDate=X&endDate=Y`
- Batch size: 500 records per page
- Only sync modified products during day
- Full sync nightly

### Overnight Sync Script Structure

```python
# blaze_sync_overnight.py
"""
Overnight sync script - runs during off-hours (2 AM - 6 AM)
Respects Blaze API rate limits strictly
"""

# Rate limit tracking
class RateLimiter:
    MAX_CALLS_PER_5MIN = 5000  # 50% of 10K limit
    calls_made = []
    
    def can_make_call(self):
        # Remove calls older than 5 minutes
        now = time.time()
        self.calls_made = [t for t in self.calls_made if now - t < 300]
        
        if len(self.calls_made) >= self.MAX_CALLS_PER_5MIN:
            return False
        return True
    
    def record_call(self):
        self.calls_made.append(time.time())

def sync_members_incremental(last_sync_time):
    """Sync members modified since last sync"""
    # Rate limit check BEFORE each call
    # Use modified date filtering
    # Batch pagination
    # Upsert to customers_blaze

def sync_transactions_incremental(last_sync_time):
    """Sync transactions modified since last sync"""
    # Rate limit check BEFORE each call
    # Use modified date filtering
    # Extract cart.items[] and save to transaction_items_blaze
    # Batch pagination
    # Upsert to transactions_blaze

def sync_products_incremental(last_sync_time):
    """Sync products modified since last sync"""
    # Rate limit check BEFORE each call
    # Use /products/modified endpoint
    # Batch pagination
    # Upsert to products_blaze

def main():
    # Load last sync time from blaze_sync_state table
    # Sync members (nightly)
    # Sync transactions (nightly)
    # Sync products (nightly)
    # Update blaze_sync_state with completion
    # Log all activity
```

### Safety Features

1. **Rate Limit Enforcement**: Hard stop if approaching limit
2. **Error Handling**: Log errors, don't crash, continue with next entity
3. **Idempotency**: Upsert on unique keys (member_id, transaction_id, product_id)
4. **Transaction Logging**: Track all syncs in `blaze_sync_state`
5. **Rollback Capability**: Keep old data until validated

---

## 📋 Implementation Checklist

### Week 1: Setup & Test
- [ ] Create mirrored tables (`customers_blaze`, `transactions_blaze`, `transaction_items_blaze`, `products_blaze`)
- [ ] Create `blaze_sync_state` tracking table
- [ ] Build test script (`blaze_api_test_small.py`)
- [ ] Run test script (10 records each)
- [ ] Verify field mappings work correctly
- [ ] Verify data inserts correctly
- [ ] Document any field mapping issues

### Week 2: Overnight Script Development
- [ ] Build `blaze_sync_overnight.py` with rate limiting
- [ ] Implement incremental sync (modified date filtering)
- [ ] Add error handling and logging
- [ ] Test with small batch (100 records each)
- [ ] Verify rate limit compliance (< 5K calls per 5min)
- [ ] Test during off-hours (2 AM test run)

### Week 3: Validation
- [ ] Run overnight sync for 1 week
- [ ] Monitor `blaze_sync_state` for errors
- [ ] Compare `customers_blaze` vs `customers` (counts, key fields)
- [ ] Compare `transactions_blaze` vs `transactions` (counts, totals)
- [ ] Document discrepancies
- [ ] Fix any data quality issues

### Week 4: Switch Preparation
- [ ] Create comparison views (old vs new)
- [ ] Validate calculated fields match
- [ ] Update dashboards to read from `*_blaze` tables (with feature flag)
- [ ] Test dashboards with new tables
- [ ] Prepare rollback plan

### Week 5: Gradual Switch
- [ ] Switch read-only queries to `*_blaze` tables
- [ ] Keep old tables as backup
- [ ] Monitor for 1 week
- [ ] If issues, switch back to old tables

### Week 6: Finalization
- [ ] Confirm new tables are stable
- [ ] Rename old tables to `*_legacy` (keep for reference)
- [ ] Rename `*_blaze` tables to production names
- [ ] Remove legacy tables (or archive)
- [ ] Document final schema

---

## 🛡️ Risk Mitigation

### Critical Protections

1. **Rate Limit**: 
   - Hard stop at 5K calls/5min (50% of limit)
   - Exponential backoff on 429 errors
   - Never exceed 10K/5min limit

2. **Data Safety**:
   - Never touch existing `customers`, `transactions`, `products` tables
   - All new data goes to `*_blaze` tables
   - Can rollback by switching back to old tables

3. **Sync Reliability**:
   - Track sync state in `blaze_sync_state`
   - Resume from last successful sync on failure
   - Never re-fetch unchanged data (use `modified` dates)

4. **Error Handling**:
   - Log all errors, don't crash
   - Continue with next entity if one fails
   - Email alerts on sync failures

---

## 📊 Expected Sync Volumes

**Conservative Estimates** (based on your data):

- **Members**: ~10,000 total → ~100 modified per day → ~10 API calls (500/page)
- **Transactions**: ~186,000 total → ~500 new per day → ~10 API calls (500/page)
- **Products**: ~3,000 total → ~50 modified per day → ~2 API calls (500/page)

**Daily Call Count**: ~22 calls (well under 5K/5min limit ✅)

**Monthly Call Count**: ~660 calls (well under 250K tier limit ✅)

---

## 🎯 Success Criteria

### Phase 1 (Tables Created)
- ✅ All `*_blaze` tables created
- ✅ Indexes created
- ✅ `blaze_sync_state` tracking table created

### Phase 2 (Test Passes)
- ✅ Test script fetches 10 records each
- ✅ Field mappings work correctly
- ✅ Data inserts successfully
- ✅ No rate limit warnings

### Phase 3 (Overnight Sync Works)
- ✅ Sync runs nightly without errors
- ✅ Rate limits respected (< 5K/5min)
- ✅ Incremental sync works (only modified records)
- ✅ All 4 entities sync successfully

### Phase 4 (Validation)
- ✅ `customers_blaze` count matches `customers` (±5%)
- ✅ Key fields match (phone, email, last_visit)
- ✅ Calculated fields match (LTV, visit counts)

### Phase 5 (Switch)
- ✅ Dashboards work with new tables
- ✅ No performance degradation
- ✅ Data quality maintained

---

## 🚀 Next Steps

1. **Review this plan** - approve approach
2. **Create tables** - run SQL schema above
3. **Build test script** - verify small batch works
4. **Test first** - don't run overnight until test passes
5. **Build overnight script** - with rate limiting
6. **Test overnight** - run once manually at 2 AM
7. **Schedule nightly** - automate after validation

---

**Remember**: 
- 🚨 Rate limit is HARD - 10K/5min max or key gets disabled
- 🧪 Test first with small batches
- 🌙 Overnight sync is safest (low traffic time)
- 📊 Use incremental sync (modified dates) from day 1
- 🔄 Parallel tables = safe rollback option



