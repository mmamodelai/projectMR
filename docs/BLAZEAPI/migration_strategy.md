# Blaze API Migration Strategy

**Goal**: Replace stale report-derived data with live Blaze API data, without breaking existing systems.

## Current State Analysis

### What We Have (Report-Derived)
- **10,047 customers** with calculated fields (`days_since_last_visit`, `lifetime_value`, `total_visits`)
- **186,394 transactions** from CSV imports
- **114,136 transaction items** (complete)
- **Calculated fields** that may be stale or inconsistent

### What Blaze API Provides
- **Live member data** with real-time updates
- **Complete transaction history** with full cart details
- **Product catalog** with real-time pricing and inventory
- **Native timestamps** (`modified`, `created`) for incremental sync

---

## Side-by-Side Field Comparison

### `customers` Table

| Your DB Column | Blaze API Field | Action | Priority | Risk |
|----------------|-----------------|--------|----------|------|
| `member_id` | `Member.id` | ✅ Direct match | High | Low |
| `name` | `firstName` + `lastName` | ✅ Concat field | High | Low |
| `phone` | `primaryPhone` | ✅ Direct match | High | Low |
| `email` | `email` | ✅ Direct match | High | Low |
| `street_address` | `address.address` | ✅ Extract from nested | High | Low |
| `city` | `address.city` | ✅ Extract from nested | High | Low |
| `state` | `address.state` | ✅ Extract from nested | High | Low |
| `zip_code` | `address.zipCode` | ✅ Extract from nested | High | Low |
| `last_visited` | `lastVisitDate` | ✅ Direct match (epoch→date) | High | Low |
| `loyalty_points` | `loyalty/member/{id}` OR infer from transactions | ⚠️ Needs endpoint test | Medium | Medium |
| `customer_type` | `status` (Active/Pending/Inactive) | ✅ Map enum | Medium | Low |
| `days_since_last_visit` | **DERIVED** from `lastVisitDate` | 🔄 Compute in DB/view | High | Low |
| `lifetime_value` | **DERIVED** from transactions | 🔄 Compute in DB/view | High | Low |
| `total_visits` | **DERIVED** from transactions | 🔄 Compute in DB/view | High | Low |
| `total_sales` | **DERIVED** from transactions | 🔄 Compute in DB/view | High | Low |
| `vip_status` | **DERIVED** from `total_visits` + `lifetime_value` | 🔄 Compute in DB/view | High | Low |
| `churn_risk` | **DERIVED** from `days_since_last_visit` | 🔄 Compute in DB/view | High | Low |

**New Fields to Add** (Augment):
- `is_medical` (boolean) ← `Member.medical`
- `text_opt_in` (boolean) ← `Member.textOptIn`
- `email_opt_in` (boolean) ← `Member.emailOptIn`
- `blaze_created` (timestamptz) ← `Member.created` (epoch ms)
- `blaze_modified` (timestamptz) ← `Member.modified` (epoch ms)

---

### `transactions` Table

| Your DB Column | Blaze API Field | Action | Priority | Risk |
|----------------|-----------------|--------|----------|------|
| `transaction_id` | `Transaction.id` | ✅ Direct match | High | Low |
| `customer_id` | `Transaction.memberId` | ✅ Direct match | High | Low |
| `date` | `Transaction.startTime` or `completedTime` | ✅ Use `completedTime` (epoch ms) | High | Low |
| `shop_location` | `Transaction.shopId` | ⚠️ Need shop lookup or store as ID | Medium | Low |
| `staff_name` | `Transaction.sellerId` | ⚠️ Need staff lookup or store as ID | Medium | Low |
| `terminal` | `Transaction.terminalId` | ✅ Direct match | Low | Low |
| `payment_type` | `Transaction.cart.paymentOption` | ✅ Extract from nested | High | Low |
| `total_amount` | `Transaction.cart.total` | ✅ Extract from nested | High | Low |
| `total_tax` | `Transaction.cart.tax` | ✅ Extract from nested | High | Low |
| `discounts` | `Transaction.cart.totalDiscount` | ✅ Extract from nested | Medium | Low |
| `loyalty_points_earned` | `Transaction.cart.pointSpent` (inverse?) | ⚠️ Needs verification | Low | Medium |
| `loyalty_points_spent` | `Transaction.cart.pointSpent` | ✅ Extract from nested | Low | Medium |

**New Fields to Add**:
- `blaze_status` (text) ← `Transaction.status` (Queued/Completed/Refund/etc.)
- `trans_type` (text) ← `Transaction.transType` (Sale/Refund/Adjustment)
- `blaze_created` (timestamptz) ← `Transaction.created`
- `blaze_modified` (timestamptz) ← `Transaction.modified`
- `start_time` (timestamptz) ← `Transaction.startTime`
- `end_time` (timestamptz) ← `Transaction.endTime`
- `completed_time` (timestamptz) ← `Transaction.completedTime`

---

### `transaction_items` Table

| Your DB Column | Blaze API Field | Action | Priority | Risk |
|----------------|-----------------|--------|----------|------|
| `transaction_id` | `OrderItem.parentId` or `Transaction.id` | ✅ Link via transaction | High | Low |
| `product_id` | `OrderItem.productId` | ✅ Direct match | High | Low |
| `product_sku` | `OrderItem.productSku` | ✅ Direct match | High | Low |
| `product_name` | `OrderItem.productName` | ✅ Direct match | High | Low |
| `brand` | `OrderItem.brandName` | ✅ Direct match | High | Low |
| `category` | `OrderItem.categoryName` | ✅ Direct match | High | Low |
| `quantity` | `OrderItem.quantity` | ✅ Direct match | High | Low |
| `unit_price` | `OrderItem.unitPrice` | ✅ Direct match | High | Low |
| `total_price` | `OrderItem.finalPrice` | ✅ Direct match (use `finalPrice`) | High | Low |

**New Fields to Add**:
- `discount` (numeric) ← `OrderItem.discount`
- `discount_type` (text) ← `OrderItem.discountType` (Cash/Percentage/FinalPrice)
- `tax` (numeric) ← `OrderItem.calcTax`
- `flower_type` (text) ← `OrderItem.weightPerUnit` or derive from product
- `strain` (text) ← Derive from product SKU/category

---

### `products` Table

| Your DB Column | Blaze API Field | Action | Priority | Risk |
|----------------|-----------------|--------|----------|------|
| `product_id` | `Product.id` | ✅ Direct match | High | Low |
| `sku` | `Product.sku` | ✅ Direct match | High | Low |
| `name` | `Product.name` | ✅ Direct match | High | Low |
| `brand` | `Product.vendorId` → need vendor lookup | ⚠️ Or store vendorId | Medium | Low |
| `category` | `Product.categoryId` → need category lookup | ⚠️ Or store categoryId | Medium | Low |
| `vendor` | `Product.vendorId` | ✅ Direct match | Medium | Low |
| `retail_price` | `Product.unitPrice` | ✅ Direct match | High | Low |
| `is_active` | `Product.active` | ✅ Direct match | High | Low |
| `thc_content` | `Product.thc` | ✅ Direct match | Medium | Low |
| `cbd_content` | `Product.cbd` | ✅ Direct match | Medium | Low |
| `cost` | **NOT IN API** | ❌ Keep existing or remove | Low | Low |

**New Fields to Add**:
- `thca` (numeric) ← `Product.thca`
- `cbda` (numeric) ← `Product.cbda`
- `cbg` (numeric) ← `Product.cbg`
- `description` (text) ← `Product.description`
- `weight_per_unit` (text) ← `Product.weightPerUnit`
- `unit_value` (numeric) ← `Product.unitValue`
- `blaze_created` (timestamptz) ← `Product.created`
- `blaze_modified` (timestamptz) ← `Product.modified`
- `image_url` (text) ← `Product.assets[0].url` (first image)

---

## Recommended Migration Path (3 Phases)

### Phase 1: **Safe Add** (Week 1-2)
**Goal**: Add new fields without touching existing data

1. **Add new columns** to tables (all nullable):
   - `customers`: `is_medical`, `text_opt_in`, `email_opt_in`, `blaze_created`, `blaze_modified`
   - `transactions`: `blaze_status`, `trans_type`, `blaze_created`, `blaze_modified`, `start_time`, `end_time`, `completed_time`
   - `transaction_items`: `discount`, `discount_type`, `tax`
   - `products`: `thca`, `cbda`, `cbg`, `description`, `weight_per_unit`, `unit_value`, `blaze_created`, `blaze_modified`, `image_url`

2. **Create staging tables**:
   - `customers_blaze_staging`
   - `transactions_blaze_staging`
   - `transaction_items_blaze_staging`
   - `products_blaze_staging`

3. **Build sync script** (Python):
   - Fetch from Blaze API (incremental: last 24h)
   - Write to staging tables
   - Validate data quality
   - **DO NOT** touch production tables yet

**Success Criteria**: Staging tables populate correctly, no errors

---

### Phase 2: **Parallel Run** (Week 3-4)
**Goal**: Run both systems side-by-side, compare results

1. **Keep syncing to staging** (hourly for members/transactions, every 5min for products)

2. **Create comparison views**:
   ```sql
   CREATE VIEW customers_comparison AS
   SELECT 
     c.member_id,
     c.name AS existing_name,
     cs.name AS blaze_name,
     c.phone AS existing_phone,
     cs.phone AS blaze_phone,
     c.last_visited AS existing_last_visit,
     cs.last_visited AS blaze_last_visit,
     c.lifetime_value AS existing_ltv,
     -- computed from blaze transactions
     (SELECT SUM(cart.total) FROM transactions_blaze_staging WHERE member_id = c.member_id) AS blaze_ltv
   FROM customers c
   LEFT JOIN customers_blaze_staging cs ON c.member_id = cs.member_id;
   ```

3. **Validate**:
   - Compare counts (should match)
   - Compare key fields (phone, email, last_visit)
   - Identify discrepancies
   - Document differences

**Success Criteria**: < 5% discrepancy on key fields, understand differences

---

### Phase 3: **Gradual Cutover** (Week 5-6)
**Goal**: Replace existing data with Blaze data, field by field

**Order of replacement** (lowest risk first):

1. **Start with fields that are 100% replaceable**:
   - `customers.phone` ← Blaze `primaryPhone`
   - `customers.email` ← Blaze `email`
   - `customers.name` ← Blaze `firstName` + `lastName`
   - `products.sku`, `products.name` ← Blaze

2. **Then replace calculated fields** (but keep old as backup):
   - Add `_old` columns: `lifetime_value_old`, `total_visits_old`
   - Copy existing values to `_old`
   - Replace with computed from Blaze transactions
   - Monitor for 1 week

3. **Finally replace derived fields**:
   - `days_since_last_visit` ← Compute from `last_visited`
   - `vip_status` ← Compute from `total_visits` + `lifetime_value`
   - `churn_risk` ← Compute from `days_since_last_visit`

**Rollback Plan**: If issues, restore from `_old` columns

---

## Critical Decisions Needed

### 1. **Staff/Location Names**
- **Option A**: Store `shopId` and `sellerId` as IDs, create lookup tables
- **Option B**: Try to resolve names via API (may not exist)
- **Option C**: Keep existing `staff_name`/`shop_location` from reports, augment with IDs

**Recommendation**: Option C (lowest risk, keeps existing data)

### 2. **Category/Brand Names**
- **Option A**: Store `categoryId`/`vendorId` as IDs, create lookup tables
- **Option B**: Fetch category/vendor names via API (if endpoints exist)
- **Option C**: Keep existing names, augment with IDs

**Recommendation**: Option C (check if vendor/category endpoints exist in swagger)

### 3. **Loyalty Points**
- **Option A**: Fetch from `/api/v1/partner/loyalty/member/{id}` (if exists)
- **Option B**: Infer from `Transaction.cart.pointSpent` (sum earned, subtract spent)
- **Option C**: Keep existing, update manually

**Recommendation**: Test Option A first, fallback to Option B

### 4. **Historical Data**
- **Option A**: Keep all existing transactions, only sync new ones going forward
- **Option B**: Replace all transactions with Blaze data
- **Option C**: Hybrid - keep existing, verify with Blaze, replace discrepancies

**Recommendation**: Option C (safest, preserves history)

---

## Implementation Checklist

### Week 1: Setup
- [ ] Add nullable columns to all tables
- [ ] Create staging tables
- [ ] Build Blaze API client (Python)
- [ ] Test API authentication
- [ ] Fetch first batch (100 records each)

### Week 2: Sync Development
- [ ] Implement incremental sync (modified windows)
- [ ] Handle pagination (skip/limit)
- [ ] Handle rate limits (429 backoff)
- [ ] Data validation (required fields, types)
- [ ] Error logging

### Week 3: Comparison
- [ ] Create comparison views
- [ ] Run side-by-side for 1 week
- [ ] Document discrepancies
- [ ] Fix data quality issues

### Week 4: Validation
- [ ] Validate field mappings
- [ ] Test edge cases (nulls, missing data)
- [ ] Performance testing (sync speed)
- [ ] User acceptance testing

### Week 5: Cutover
- [ ] Replace safe fields (phone, email, name)
- [ ] Monitor for errors
- [ ] Replace calculated fields (with backup)
- [ ] Monitor for 1 week

### Week 6: Finalization
- [ ] Remove staging tables (or keep for audit)
- [ ] Remove backup columns (`_old`)
- [ ] Document final schema
- [ ] Update dashboards/queries

---

## Risk Mitigation

### High Risk Areas
1. **Field name mismatches** → Test with small batch first
2. **Data type conversions** → Validate epoch→timestamp, null handling
3. **Missing data** → Handle nulls gracefully, don't overwrite with nulls
4. **Rate limits** → Implement exponential backoff, respect 10K/5min limit
5. **API downtime** → Fail gracefully, retry later, don't break production

### Low Risk Areas
- Adding new nullable columns ✅
- Fetching read-only data ✅
- Staging tables ✅

---

## Expected Outcomes

### Immediate Benefits
- ✅ Real-time customer data (phone, email, address)
- ✅ Accurate `last_visited` dates
- ✅ Live product pricing
- ✅ Current transaction status

### Medium-Term Benefits
- ✅ Accurate calculated fields (LTV, visit counts)
- ✅ Better segmentation (VIP, churn risk)
- ✅ Real-time product availability

### Long-Term Benefits
- ✅ No more CSV imports
- ✅ Single source of truth
- ✅ Faster data updates
- ✅ Better data quality

---

## Next Steps

1. **Review this document** - approve/revise approach
2. **Test API endpoints** - verify loyalty, vendor, category endpoints exist
3. **Build Phase 1** - add columns, create staging tables
4. **Start sync** - begin populating staging tables
5. **Compare** - validate data quality before cutover

---

**Questions to Answer**:
- [ ] Do vendor/category lookup endpoints exist?
- [ ] Do staff lookup endpoints exist?
- [ ] What's the loyalty points endpoint structure?
- [ ] Should we keep historical CSV data or replace entirely?
- [ ] What's the rollback plan if data quality issues?



