# 🚀 Leafly → Supabase: Execution Runbook

**Purpose**: Step-by-step guide to execute the Leafly integration  
**Audience**: Anyone who needs to run this process  
**Time**: 15-20 minutes total

---

## ✅ Pre-Flight Checklist

Before starting, verify:

- [ ] Supabase database accessible
- [ ] Source data exists: `Data/inventory_enhanced_v2.json`
- [ ] Python 3.7+ installed
- [ ] Required packages: `supabase`, `fuzzywuzzy`, `python-levenshtein`
- [ ] Supabase service_role key available

---

## 📋 Step-by-Step Execution

### **STEP 1: Schema Changes (COMPLETED ✅)**

**Status**: Already done via Supabase MCP

**What was added**:
- 14 new columns to `products` table
- 5 GIN indexes for fast array searches
- 1 view (`products_with_leafly`)

**Verification**:
```sql
-- Check columns exist
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'products' 
AND column_name IN ('effects', 'helps_with', 'leafly_description');
```

Expected: 3 rows returned

---

### **STEP 2: Data Import (NEXT)**

#### Option A: Automated Import (Recommended)

**If Supabase API access is available:**

1. Load source data:
   ```python
   import json
   with open('Data/inventory_enhanced_v2.json') as f:
       leafly_data = json.load(f)
   ```

2. Connect to Supabase:
   ```python
   from supabase import create_client
   supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
   ```

3. Fetch products:
   ```python
   products = supabase.table('products').select('*').execute()
   ```

4. Match and update:
   ```python
   for strain in leafly_data:
       matches = match_strain_to_products(strain['name'], products)
       for product, confidence in matches:
           if confidence >= 85:
               update_product(product, strain)
   ```

#### Option B: Manual Script Execution

1. **Edit the import script**:
   ```bash
   cd mota-crm/import_tools
   code import_leafly_data.py
   ```

2. **Update line 24** with your Supabase key:
   ```python
   SUPABASE_KEY = 'your-service-role-key-here'
   ```

3. **Run the import**:
   ```bash
   python import_leafly_data.py
   ```

4. **Watch the output**:
   ```
   [1/24] Gelato #41
   ✅ Found 1,443 matches
   📝 Updating products...
   ...
   ```

---

### **STEP 3: Verification**

#### Check 1: Count Updated Products

```sql
SELECT COUNT(*) as products_with_leafly
FROM products
WHERE leafly_description IS NOT NULL;
```

**Expected**: 8,000-10,000 products

#### Check 2: Sample Data

```sql
SELECT 
    name,
    LEFT(leafly_description, 50) as description_sample,
    effects,
    helps_with,
    leafly_rating
FROM products
WHERE leafly_description IS NOT NULL
LIMIT 5;
```

**Expected**: 5 rows with rich data

#### Check 3: Test Array Queries

```sql
-- Find products that help with anxiety
SELECT COUNT(*)
FROM products
WHERE 'Anxiety' = ANY(helps_with);
```

**Expected**: 1,000+ products

```sql
-- Find products with "Relaxed" effect
SELECT COUNT(*)
FROM products
WHERE 'Relaxed' = ANY(effects);
```

**Expected**: 2,000+ products

#### Check 4: Verify by Category

```sql
SELECT 
    category,
    COUNT(*) as total,
    COUNT(leafly_description) as with_leafly
FROM products
GROUP BY category
ORDER BY with_leafly DESC;
```

**Expected Top Results**:
- Flower PrePacks: 5,000+ with Leafly
- Vapes: 2,000+ with Leafly
- Concentrates: 500+ with Leafly

#### Check 5: View Functionality

```sql
SELECT COUNT(*) 
FROM products_with_leafly
WHERE has_leafly_data = true;
```

**Expected**: Same as Check 1

---

### **STEP 4: Post-Import Actions**

#### Update WORKLOG
```markdown
## [DATE] - Leafly Integration Complete

### Results:
- Products updated: [actual count]
- Strains processed: 24
- Success rate: [percentage]

### Verification:
- ✅ All checks passed
- ✅ Array queries working
- ✅ View functional
```

#### Test AI Queries

**Query 1**: "What helps with anxiety?"
```sql
SELECT name, helps_with, effects
FROM products_with_leafly
WHERE 'Anxiety' = ANY(helps_with)
AND is_active = true
LIMIT 5;
```

**Query 2**: "Show me Gelato products"
```sql
SELECT name, leafly_description, effects
FROM products_with_leafly
WHERE name ILIKE '%gelato%'
AND leafly_description IS NOT NULL
LIMIT 5;
```

**Query 3**: "Relaxing strains"
```sql
SELECT name, effects, strain_type
FROM products_with_leafly
WHERE 'Relaxed' = ANY(effects)
LIMIT 5;
```

---

## 📊 Expected Results Summary

### By the Numbers:

| Metric | Expected Value |
|--------|---------------|
| Products Updated | 8,000-10,000 |
| Strains Processed | 24 |
| Success Rate | 95%+ |
| Categories Affected | 7 |
| Import Time | 5-10 minutes |

### By Strain (Top 5):

| Strain | Products Updated |
|--------|-----------------|
| Gelato | ~1,443 |
| Runtz | ~1,408 |
| OG | ~1,079 |
| Lemon variants | ~518 |
| Motor Breath | ~500 |

---

## 🚨 Troubleshooting

### Issue: Few or No Matches Found

**Symptoms**:
```
[1/24] Gelato #41
  ❌ No matches found
```

**Solutions**:
1. Check product names contain strain names
2. Adjust normalization function
3. Lower confidence threshold (85% → 80%)
4. Check for typos in strain names

### Issue: Import Errors

**Symptoms**:
```
❌ Error updating product: [error message]
```

**Solutions**:
1. Check Supabase API key is service_role (not anon)
2. Verify network connection
3. Check Supabase table permissions
4. Look for rate limiting

### Issue: Slow Import

**Symptoms**:
- Import taking >20 minutes

**Solutions**:
1. Normal for 8,000+ products
2. Consider batch updates (100 at a time)
3. Check Supabase performance dashboard

### Issue: Wrong Data Imported

**Symptoms**:
- Ice Cream Cake has Gelato description

**Solutions**:
1. Check matching algorithm
2. Verify normalized names
3. Review confidence scores
4. Run rollback (see Technical doc)

---

## 🔄 Re-Running the Import

### To Update Existing Data:

The import script is **idempotent** - safe to run multiple times:

```python
# The UPDATE statement will overwrite existing data
UPDATE products
SET leafly_description = ...,
    effects = ...,
    ...
WHERE id = product_id;
```

### To Add New Strains:

1. Add new strains to `Data/inventory_enhanced_v2.json`
2. Re-run import script
3. Only new matches will be processed

### To Fix Specific Products:

```sql
-- Clear specific product
UPDATE products
SET leafly_description = NULL,
    effects = NULL,
    helps_with = NULL,
    flavors = NULL,
    terpenes = NULL
WHERE name ILIKE '%specific product%';

-- Re-run import for that strain
```

---

## 📝 Completion Checklist

After successful import:

- [ ] 8,000-10,000 products updated
- [ ] All 5 verification checks passed
- [ ] Array queries working
- [ ] View functional
- [ ] Sample queries return expected data
- [ ] WORKLOG.md updated
- [ ] Team notified of new capabilities

---

## 🎯 Next Steps

After successful integration:

1. **Update MotaBot AI**:
   - Add effect-based queries
   - Enable medical use case filtering
   - Implement flavor preferences

2. **Enhance CRM Viewers**:
   - Display Leafly descriptions
   - Show effects and flavors
   - Add product images

3. **Marketing Campaigns**:
   - Create effect-based collections
   - Medical use case promotions
   - Educated customer content

4. **Expand Dataset**:
   - Scrape more Leafly strains
   - Add 50-100 more strains
   - Eventually cover full inventory

---

**Runbook Version**: 1.0  
**Last Updated**: October 14, 2025  
**Status**: Ready for execution  
**Estimated Time**: 15-20 minutes  
**Success Rate**: 95%+



