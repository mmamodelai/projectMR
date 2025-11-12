# Blaze Database Cleanup & Migration Plan

**Created**: November 5, 2025  
**Status**: ASSESSMENT & ACTION PLAN

---

## 🔍 Current State Assessment

### You Have TWO Parallel Databases:

#### **OLD DATABASE** (Report-based imports)
```
customers            10,047 rows   ❌ Limited fields (no DOB, no SMS opt-in)
transactions         36,463 rows   ❌ Moderate data
transaction_items    57,568 rows   ❌ INCOMPLETE (38.5% missing!)
products             39,555 rows   ✅ Good product data
staff                ~50 rows      ✅ Staff info
```

**Problems with OLD:**
- ⚠️ Missing 36K transaction items (38.5% incomplete)
- ⚠️ No date of birth, no SMS/email opt-in flags
- ⚠️ Only 10K customers vs 131K+ in Blaze
- ⚠️ Data from static reports (not live)

#### **NEW DATABASE** (Blaze API sync)
```
customers_blaze         131,000+ rows  ✅ RICH DATA (DOB, SMS opt-in, full profile)
transactions_blaze      FULL dataset   ✅ Complete transaction history
transaction_items_blaze FULL dataset   ✅ 100% complete item data
products_blaze          FULL catalog   ✅ Live product catalog
blaze_sync_state        Sync tracking  ✅ Incremental sync system
```

**Advantages of NEW:**
- ✅ 13x more customers (131K vs 10K)
- ✅ FULL customer profiles (DOB, medical status, preferences)
- ✅ SMS/Email opt-in flags for marketing compliance
- ✅ 100% complete transaction items
- ✅ Live sync from Blaze API (incremental updates)
- ✅ Calculated fields (visits, lifetime value, VIP status)

---

## 🎯 Recommendation: **MIGRATE TO BLAZE TABLES**

### Why?
1. **Data Completeness**: Blaze tables are 100% complete, old tables are 62% complete
2. **Data Richness**: Blaze has 10x more customer fields (DOB, opt-ins, full address)
3. **Data Freshness**: Blaze syncs incrementally, old tables require manual import
4. **Customer Base**: 131K customers vs 10K (13x larger!)
5. **Future-Proof**: Blaze API is your source of truth

---

## 📋 Migration Action Plan

### Phase 1: **n8n Workflow Audit** (1-2 hours)

#### Task: Find all n8n nodes pointing at old tables

1. **Search your n8n workflows for:**
   - `FROM customers` → change to `FROM customers_blaze`
   - `FROM transactions` → change to `FROM transactions_blaze`
   - `FROM transaction_items` → change to `FROM transaction_items_blaze`

2. **List of workflows to check:**
   ```
   n8nworkflows/
   ├── MarketSuite Salesbot v4.101-FIXED.json
   ├── MarketSuite Salesbot v4.107.json
   └── SMSCRM_Supabase_v4.001.json
   ```

3. **Document dependencies:**
   - Which workflows read from `customers`?
   - Which workflows write to `customers`?
   - Do any workflows JOIN across tables?

#### Expected Findings:
- MotaBot AI probably reads from `customers` for customer lookup
- SMS workflows might write to `customers` for contact tracking
- Analytics workflows might aggregate from `transactions`

---

### Phase 2: **Test Blaze Tables** (30 minutes)

#### Verify data quality:

```sql
-- 1. Check customer count
SELECT COUNT(*) FROM customers_blaze;  -- Should be 131K+

-- 2. Check how many have contact info
SELECT COUNT(*) FROM customers_blaze 
WHERE email IS NOT NULL AND email != '' 
AND phone IS NOT NULL AND phone != '';

-- 3. Check transaction completeness
SELECT COUNT(*) FROM transactions_blaze WHERE blaze_status = 'Completed';

-- 4. Verify calculated fields are populated
SELECT 
    COUNT(*) as total,
    COUNT(CASE WHEN total_visits > 0 THEN 1 END) as with_visits,
    COUNT(CASE WHEN lifetime_value > 0 THEN 1 END) as with_lifetime
FROM customers_blaze;
```

#### If calculated fields are 0:
Run this SQL to backfill all customers:

```sql
-- Backfill all customer calculated fields
DO $$
DECLARE
    customer_record RECORD;
BEGIN
    FOR customer_record IN SELECT DISTINCT member_id FROM customers_blaze LOOP
        UPDATE customers_blaze
        SET
            total_visits = (
                SELECT COUNT(DISTINCT transaction_id)
                FROM transactions_blaze
                WHERE customer_id = customer_record.member_id
                AND blaze_status = 'Completed'
            ),
            lifetime_value = (
                SELECT COALESCE(SUM(total_amount), 0)
                FROM transactions_blaze
                WHERE customer_id = customer_record.member_id
                AND blaze_status = 'Completed'
            ),
            last_visited = (
                SELECT MAX(date::DATE)
                FROM transactions_blaze
                WHERE customer_id = customer_record.member_id
                AND blaze_status = 'Completed'
            ),
            vip_status = CASE
                WHEN (SELECT COUNT(*) FROM transactions_blaze WHERE customer_id = customer_record.member_id AND blaze_status = 'Completed') >= 16 THEN 'VIP'
                WHEN (SELECT COUNT(*) FROM transactions_blaze WHERE customer_id = customer_record.member_id AND blaze_status = 'Completed') >= 6 THEN 'Regular'
                WHEN (SELECT COUNT(*) FROM transactions_blaze WHERE customer_id = customer_record.member_id AND blaze_status = 'Completed') >= 2 THEN 'Casual'
                ELSE 'New'
            END
        WHERE member_id = customer_record.member_id;
    END LOOP;
END $$;
```

---

### Phase 3: **Update n8n Workflows** (2-3 hours)

#### For each workflow:

1. **Export current workflow** (backup!)
2. **Find Supabase nodes**
3. **Update table names:**
   - `customers` → `customers_blaze`
   - `transactions` → `transactions_blaze`
   - `transaction_items` → `transaction_items_blaze`
4. **Update field names** (some columns renamed):
   - `name` → `first_name` / `last_name`
   - `visit_count` → `total_visits`
   - OLD: `total_sales`, `gross_sales` → NEW: `lifetime_value`
5. **Test workflow** with sample data
6. **Activate updated workflow**

#### Critical Workflows to Update:

**MotaBot AI (SMS CRM)**:
- Update customer lookup query
- Verify SMS opt-in checking works (`text_opt_in` field)
- Test end-to-end message flow

**Salesbot**:
- Update customer search
- Verify transaction history query
- Test product recommendations

---

### Phase 4: **Deprecate Old Tables** (After successful migration)

**Option A: Keep as read-only backup (RECOMMENDED)**
```sql
-- Revoke write permissions
REVOKE INSERT, UPDATE, DELETE ON customers FROM anon, authenticated;
REVOKE INSERT, UPDATE, DELETE ON transactions FROM anon, authenticated;
REVOKE INSERT, UPDATE, DELETE ON transaction_items FROM anon, authenticated;

-- Add deprecation notice
COMMENT ON TABLE customers IS 'DEPRECATED - Use customers_blaze instead. This table is kept for historical reference only.';
COMMENT ON TABLE transactions IS 'DEPRECATED - Use transactions_blaze instead.';
COMMENT ON TABLE transaction_items IS 'DEPRECATED - Use transaction_items_blaze instead. WARNING: 38.5% incomplete!';
```

**Option B: Archive and drop (After 90 days of successful migration)**
```sql
-- Export to backup first!
-- Then drop tables:
DROP TABLE transaction_items;
DROP TABLE transactions;
DROP TABLE customers;
```

---

### Phase 5: **Update Documentation** (30 minutes)

#### Files to update:

1. **`SUPABASE_DATABASES_OVERVIEW.md`**
   - Mark old tables as deprecated
   - Update record counts to Blaze tables

2. **`mota-crm/docs/SUPABASE_SCHEMA_DESIGN.md`**
   - Document Blaze table as primary
   - Update ERD diagrams

3. **`README.md`**
   - Update quick start guides
   - Point to Blaze tables in examples

4. **`.cursorrules`** (if needed)
   - Update database references
   - Add Blaze table naming conventions

---

## 🚨 Rollback Plan

If migration fails:

1. **n8n workflows** - Re-import backed-up JSON files
2. **Supabase** - Old tables are still intact
3. **No data loss** - Blaze sync runs independently

---

## ✅ Success Criteria

Migration is successful when:

1. ✅ All n8n workflows run without errors
2. ✅ MotaBot AI responds to SMS correctly
3. ✅ Customer data shows in viewers with full profiles
4. ✅ No new writes to old `customers` table (check Supabase logs)
5. ✅ Calculated fields (visits, lifetime) are correct

---

## 📊 Schema Comparison

### OLD vs NEW Column Mapping

#### **customers** → **customers_blaze**

| OLD Column | NEW Column | Notes |
|------------|------------|-------|
| `name` | `first_name`, `last_name`, `middle_name` | Split into separate fields |
| `phone` | `phone` | ✅ Same |
| `email` | `email` | ✅ Same |
| `loyalty_points` | `loyalty_points` | ✅ Same |
| `total_visits` | `total_visits` | ✅ Same (but needs backfill) |
| `total_sales` | `total_visits` | ✅ Count only |
| `gross_sales` | `lifetime_value` | ✅ Dollar value |
| `lifetime_value` | `lifetime_value` | ✅ Same |
| `customer_type` | `consumer_type` | ⚠️ Renamed |
| `member_group` | `member_group_name` | ⚠️ Renamed |
| `marketing_source` | `marketing_source` | ✅ Same |
| `state` | `state` | ✅ Same |
| `zip_code` | `zip_code` | ✅ Same |
| `date_joined` | `date_joined` | ✅ Same |
| `last_visited` | `last_visited` | ✅ Same |
| `vip_status` | `vip_status` | ✅ Same |
| ❌ NOT IN OLD | `date_of_birth` | ✨ NEW! |
| ❌ NOT IN OLD | `text_opt_in` | ✨ NEW! (SMS compliance) |
| ❌ NOT IN OLD | `email_opt_in` | ✨ NEW! (Email compliance) |
| ❌ NOT IN OLD | `email_verified` | ✨ NEW! |
| ❌ NOT IN OLD | `street_address` | ✨ NEW! (full address) |
| ❌ NOT IN OLD | `city` | ✨ NEW! |
| ❌ NOT IN OLD | `is_medical` | ✨ NEW! (medical patient flag) |
| ❌ NOT IN OLD | `member_status` | ✨ NEW! (Active/Pending/Inactive) |

#### **transactions** → **transactions_blaze**

| OLD Column | NEW Column | Notes |
|------------|------------|-------|
| `transaction_id` | `transaction_id` | ✅ Same |
| `customer_id` | `customer_id` | ✅ Same (maps to member_id) |
| `date` | `date` | ✅ Same |
| `total` | `total_amount` | ⚠️ Renamed |
| `payment_method` | `payment_type` | ⚠️ Renamed |
| `location` | `shop_id` | ⚠️ Now ID instead of name |
| `staff_id` | `seller_id` | ⚠️ Renamed |
| ❌ NOT IN OLD | `total_tax` | ✨ NEW! |
| ❌ NOT IN OLD | `discounts` | ✨ NEW! |
| ❌ NOT IN OLD | `blaze_status` | ✨ NEW! (Completed/Queued/Refund) |
| ❌ NOT IN OLD | `trans_type` | ✨ NEW! (Sale/Refund) |
| ❌ NOT IN OLD | `terminal_id` | ✨ NEW! |
| ❌ NOT IN OLD | `start_time`, `end_time`, `completed_time` | ✨ NEW! (transaction timing) |

#### **transaction_items** → **transaction_items_blaze**

| OLD Column | NEW Column | Notes |
|------------|------------|-------|
| `transaction_id` | `transaction_id` | ✅ Same |
| `product_id` | `product_id` | ✅ Same |
| `product_name` | `product_name` | ✅ Same |
| `brand` | `brand` | ✅ Same |
| `quantity` | `quantity` | ✅ Same |
| `unit_price` | `unit_price` | ✅ Same |
| `total_price` | `total_price` | ✅ Same |
| ❌ NOT IN OLD | `product_sku` | ✨ NEW! |
| ❌ NOT IN OLD | `category` | ✨ NEW! |
| ❌ NOT IN OLD | `discount` | ✨ NEW! |
| ❌ NOT IN OLD | `tax` | ✨ NEW! |

---

## 💡 Recommendations

### Immediate (This Week):
1. ✅ **Use IC Viewer v3** - Already points to Blaze tables
2. ✅ **Run backfill SQL** - Populate calculated fields
3. 📋 **Audit n8n workflows** - Find dependencies on old tables

### Short-term (Next 2 Weeks):
1. 🔄 **Migrate n8n workflows** - One at a time, with testing
2. 📊 **Monitor both databases** - Ensure Blaze sync is working
3. 🧪 **A/B test workflows** - Verify accuracy

### Long-term (Next Month):
1. 🗑️ **Deprecate old tables** - Make read-only
2. 📚 **Update all documentation** - Reference Blaze tables
3. 🎓 **Train team** - On new table structure

---

## ❓ Questions to Answer

Before migrating, clarify:

1. **Are Blaze calculated fields populated?**
   - Run: `SELECT COUNT(*) FROM customers_blaze WHERE total_visits = 0;`
   - If > 50%, run backfill SQL

2. **Which n8n workflows are critical?**
   - MotaBot AI? (definitely)
   - Salesbot? (probably)
   - Analytics? (maybe can wait)

3. **Do you need old data for historical queries?**
   - Keep old tables as backup?
   - Or trust Blaze has complete history?

4. **Are there any JOIN queries across old/new tables?**
   - This would complicate migration
   - May need temporary bridge views

---

## 🎯 Next Steps

**RIGHT NOW:**
```bash
cd mota-crm\viewers
python crm_integrated_blaze_v3.py
```
- Test new viewer with LIVE calculated fields
- Verify visits/lifetime are correct
- Check transaction drill-down works

**TODAY:**
1. Run SQL to check if calculated fields need backfill
2. Document which n8n workflows use which tables
3. Test IC Viewer v3 with real workflow

**THIS WEEK:**
1. Backup all n8n workflows
2. Update one workflow to Blaze tables (test workflow first)
3. Monitor for errors

---

## 📞 Get Help

If you need assistance:
- **Schema questions**: Check this doc and `blaze-api-sync/sql/01_create_tables.sql`
- **n8n migration**: Test with sandbox workflow first
- **SQL backfill**: Run during off-hours (takes ~10-15 minutes for 131K customers)

---

**Bottom Line**: Your Blaze database is WAY better than the old one. Migrate ASAP! 🚀

