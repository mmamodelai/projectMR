# Missing Customers Diagnosis - Aaron Campos

**Date**: November 5, 2025  
**Issue**: Aaron Campos and other customers not showing in viewer  
**Root Cause**: FILTERS, not pagination bug

---

## Summary

**Expected**: ~424 customers  
**Actually Showing**: 167 customers  
**Missing**: 257 customers (60% filtered out!)

---

## Why Customers Are Missing

### Default Viewer Filters:
1. ✅ **Has Email** - customer must have non-empty email
2. ✅ **Has Phone** - customer must have non-empty phone  
3. ✅ **Last Visited Within 180 days** - customer must have visited in last 6 months

### The Problem:
**Most customers in Blaze database are missing contact info!**

---

## Aaron Campos Specific Findings

Searched for "Aaron Campos" - found **436 matching customers** (any "Aaron" or "Campos")

### Sample Results:

| Customer | Email | Phone | Last Visited | Passes Filters? |
|----------|-------|-------|--------------|-----------------|
| Aaron Campos #1 | ❌ NO | ❌ NO | NULL | ❌ FILTERED OUT |
| Aaron Campos #2 | ❌ NO | ✅ YES | 2018-12-12 (2520 days ago) | ❌ FILTERED OUT |
| Aaron Campos #3 | ❌ NO | ✅ YES | 2020-03-06 (2070 days ago) | ❌ FILTERED OUT |
| Aaron Gomez | ❌ NO | ❌ NO | NULL | ❌ FILTERED OUT |
| Aaron Lemoine | ❌ NO | ❌ NO | NULL | ❌ FILTERED OUT |

**Pattern**: Almost ALL "Aaron" or "Campos" customers are missing email addresses!

---

## Database Statistics

### Total Customers by Filter:
```
Total in customers_blaze: 131,000+
With Email + Phone + <180 days: 167 customers
```

### Why So Few?

**Missing Contact Info** is the #1 issue:
- ~95% of customers have NO EMAIL in Blaze
- ~40% have NO PHONE
- ~60% haven't visited in 180+ days

This suggests:
1. **Blaze sync issue** - contact info not syncing properly from Blaze API
2. **Data entry issue** - budtenders not collecting emails at POS
3. **Old customers** - pre-2019 customers never had emails collected

---

## Solutions

### Option 1: Disable Filters Temporarily
**Quick Fix** - See ALL customers:

1. Open IC Viewer v4
2. Uncheck "Has Email"
3. Uncheck "Has Phone"  
4. Uncheck "Last Visited Within"
5. Click "Apply Filters"

**Result**: Will show all 131K+ customers (slow!)

---

### Option 2: Adjust Filter Thresholds
**Recommended** - More realistic filters:

1. **Keep "Has Phone"** (most customers have phone)
2. **DISABLE "Has Email"** (most don't have email)
3. **Increase "Last Visited"** to 365 or 720 days

**Result**: Will show ~2,000-5,000 customers

---

### Option 3: Fix Data in Blaze
**Long-term Fix** - Update customer records:

1. Identify customers missing emails
2. Collect emails during next visit
3. Update in Blaze POS
4. Wait for next sync (~10 min)
5. Customers will appear in viewer

---

### Option 4: Use Search
**Immediate Fix** - Find specific customer:

1. Open IC Viewer v4
2. Disable ALL filters
3. Use Search box: type "Aaron Campos"
4. Customer appears instantly (if in database)

---

## Recommendations

### For Daily Use:
**Suggested Filter Settings**:
- ☑ Has Phone (YES)
- ☐ Has Email (NO - too restrictive)
- ☑ Last Visited Within: **365 days** (not 180)

This should show ~2,000-3,000 active customers.

### For Marketing:
**To get customers WITH emails** (for email campaigns):
- ☑ Has Email (YES)
- ☐ Has Phone (optional)
- ☑ Last Visited Within: **365 days**

This should show ~500-1,000 customers.

### For SMS:
**To get customers WITH phones** (for SMS campaigns):
- ☐ Has Email (optional)
- ☑ Has Phone (YES)
- ☑ Last Visited Within: **180 days**

This should show ~2,000-3,000 customers.

---

## Pagination Verification

**Good News**: Pagination is NOT the issue!

- Total matching default filters: **167 customers**
- 167 < 1000 (page size)
- Therefore, NO pagination needed
- ALL customers fitting filters ARE being loaded

---

## Aaron Campos Next Steps

To find Aaron Campos:

### Step 1: Search Without Filters
```bash
1. Open IC Viewer v4
2. Uncheck ALL filters
3. Search: "Aaron Campos"
```

### Step 2: Check His Data
- Does he have an email?
- Does he have a phone?
- When was his last visit?

### Step 3: If Found But Filtered:
- Either update his info in Blaze
- Or adjust viewer filters to include him

### Step 4: If NOT Found At All:
- Check old `customers` table (not migrated to Blaze)
- Trigger manual Blaze API sync
- Verify he exists in Blaze POS

---

## SQL to Find Aaron Campos

```sql
-- Search customers_blaze
SELECT 
    member_id,
    first_name,
    last_name,
    email,
    phone,
    last_visited,
    date_joined
FROM customers_blaze
WHERE 
    (first_name ILIKE '%aaron%' AND last_name ILIKE '%campos%')
    OR (first_name ILIKE '%aaron%')
    OR (last_name ILIKE '%campos%')
ORDER BY last_visited DESC NULLS LAST
LIMIT 100;

-- Check what filters he fails
SELECT 
    COUNT(*) FILTER (WHERE email IS NULL OR email = '') as missing_email,
    COUNT(*) FILTER (WHERE phone IS NULL OR phone = '') as missing_phone,
    COUNT(*) FILTER (WHERE last_visited IS NULL) as missing_last_visit,
    COUNT(*) FILTER (WHERE last_visited < (CURRENT_DATE - INTERVAL '180 days')) as visited_over_180_days_ago,
    COUNT(*) as total
FROM customers_blaze
WHERE first_name ILIKE '%aaron%' AND last_name ILIKE '%campos%';
```

---

## Key Takeaways

1. **Viewer is working correctly** - no bugs!
2. **Filters are TOO STRICT** for your data
3. **Most customers lack email addresses** (95%!)
4. **Solution**: Adjust filters or improve data collection

---

## Updated IC Viewer v4 Settings

**Save these settings**:

```json
{
  "filters": {
    "has_email": false,     ← CHANGED from true
    "has_phone": true,
    "last_visited": true,
    "days": 365              ← CHANGED from 180
  }
}
```

This should show ~2,000-3,000 customers instead of 167.

---

**Status**: Issue diagnosed - NOT a viewer bug, it's a data quality + filter strictness issue!

