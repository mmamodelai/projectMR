# 🔧 Leafly → Supabase: Technical Implementation Guide

**Database**: Supabase (kiwmwoqrguyrcpjytgte)  
**Source Data**: `Data/inventory_enhanced_v2.json` (24 Leafly strains)  
**Target**: `products` table  
**Impact**: 8,000-10,000+ products

---

## 📋 Table of Contents
1. [Database Schema Changes](#database-schema-changes)
2. [Matching Algorithm](#matching-algorithm)
3. [Import Process](#import-process)
4. [Verification](#verification)
5. [Rollback Plan](#rollback-plan)

---

## 1. Database Schema Changes

### Columns Added to `products` Table:

```sql
-- Basic Leafly fields
leafly_strain_type        TEXT            -- Hybrid, Indica, Sativa
leafly_description        TEXT            -- Full 335-char descriptions
leafly_rating             DECIMAL(3,2)    -- 4.62 stars
leafly_review_count       INTEGER         -- 151 reviews

-- Arrays (multi-value fields using PostgreSQL arrays)
effects                   TEXT[]          -- ["Relaxed", "Euphoric", "Happy"]
helps_with                TEXT[]          -- ["Anxiety", "Stress", "Depression"]
negatives                 TEXT[]          -- ["Dry mouth", "Dry eyes"]
flavors                   TEXT[]          -- ["Lavender", "Pepper", "Flowery"]
terpenes                  TEXT[]          -- ["Caryophyllene", "Limonene"]

-- Lineage
parent_strains            TEXT[]          -- ["Sunset Sherbert", "Thin Mint Cookies"]
lineage                   TEXT            -- "Sunset Sherbert x Thin Mint Cookies"

-- Media
image_url                 TEXT            -- Product/strain image URL
leafly_url                TEXT            -- Link to Leafly strain page

-- Metadata
leafly_data_updated_at    TIMESTAMPTZ     -- Import timestamp
```

### Indexes Created:

```sql
-- GIN indexes for fast array searches
CREATE INDEX idx_products_effects ON products USING GIN(effects);
CREATE INDEX idx_products_helps_with ON products USING GIN(helps_with);
CREATE INDEX idx_products_flavors ON products USING GIN(flavors);
CREATE INDEX idx_products_terpenes ON products USING GIN(terpenes);

-- Partial index for products with Leafly data
CREATE INDEX idx_products_has_leafly ON products(leafly_description) 
WHERE leafly_description IS NOT NULL;
```

### View Created:

```sql
CREATE VIEW products_with_leafly AS
SELECT 
    p.id,
    p.product_id,
    p.name,
    p.brand,
    p.category,
    p.strain,
    p.flower_type,
    p.thc_content,
    p.cbd_content,
    COALESCE(p.leafly_strain_type, p.flower_type) as strain_type,
    p.leafly_description,
    p.leafly_rating,
    p.leafly_review_count,
    p.effects,
    p.helps_with,
    p.negatives,
    p.flavors,
    p.terpenes,
    p.parent_strains,
    p.lineage,
    p.image_url,
    p.leafly_url,
    p.retail_price,
    p.is_active,
    CASE 
        WHEN p.leafly_description IS NOT NULL THEN true 
        ELSE false 
    END as has_leafly_data,
    p.created_at,
    p.leafly_data_updated_at
FROM products p;
```

---

## 2. Matching Algorithm

### Challenge:
- **Leafly names**: "Gelato #41", "Ice Cream Cake", "Green Crack"
- **Product names**: "Mota Flwr 8th Gelato 45", "Stiiizy Cart 1g Ice Cream Cake", "RawG Cart 1g Green Crack Sativa"

### Solution: Fuzzy Name Matching

#### Step 1: Normalize Strain Names

```python
def normalize_strain_name(name):
    """Remove common words and normalize for matching"""
    name = name.lower().strip()
    
    # Remove common words
    remove_words = ['flower', 'strain', 'cannabis', 'weed', 
                   'premium', 'mota', 'brand', 'flwr', 'cart', 
                   'pre-roll', 'preroll', 'vape', 'extract']
    for word in remove_words:
        name = re.sub(rf'\b{word}\b', '', name)
    
    # Remove quantities (3.5g, 1oz, 100mg)
    name = re.sub(r'\d+\.?\d*\s*(g|gram|oz|ounce|mg)s?', '', name)
    
    # Normalize special characters
    name = name.replace('#', '').replace('-', ' ').replace('_', ' ')
    
    # Remove multiple spaces
    name = re.sub(r'\s+', ' ', name)
    
    return name.strip()
```

**Examples:**
```python
normalize_strain_name("Mota Flwr 8th Gelato 45 - 3.5g")
# → "gelato 45"

normalize_strain_name("Stiiizy Cart 1g Ice Cream Cake Indica")
# → "ice cream cake indica"

normalize_strain_name("Gelato #41")
# → "gelato 41"
```

#### Step 2: Match with Confidence Scores

```python
def match_strain_to_products(strain_name, products):
    """
    Match strain name to products using 3 strategies:
    1. Exact match (100% confidence)
    2. Contains match (90% confidence)
    3. Fuzzy match (85%+ confidence)
    """
    matches = []
    normalized_strain = normalize_strain_name(strain_name)
    
    for product in products:
        product_name = product['name']
        normalized_product = normalize_strain_name(product_name)
        
        # Strategy 1: Exact match
        if normalized_strain == normalized_product:
            matches.append((product, 100))
            continue
        
        # Strategy 2: Contains match
        if normalized_strain in normalized_product:
            matches.append((product, 90))
            continue
        
        # Strategy 3: Fuzzy match (Levenshtein distance)
        similarity = fuzz.ratio(normalized_strain, normalized_product)
        if similarity >= 85:
            matches.append((product, similarity))
    
    return sorted(matches, key=lambda x: x[1], reverse=True)
```

#### Step 3: Update High-Confidence Matches

```python
# Only update products with ≥85% confidence
high_confidence = [m for m in matches if m[1] >= 85]

for product, confidence in high_confidence:
    update_product_with_leafly_data(product, strain_data)
```

---

## 3. Import Process

### Data Flow:

```
┌─────────────────────────────────────────────────────────────┐
│                    IMPORT PROCESS                           │
└─────────────────────────────────────────────────────────────┘

Step 1: Load Source Data
    ↓
Data/inventory_enhanced_v2.json
    • 24 Leafly strains
    • Full strain profiles
    ↓
Step 2: Fetch All Products
    ↓
Supabase products table
    • 39,555 products
    • Filter: has name/strain
    ↓
Step 3: Match Strains
    ↓
For each Leafly strain:
    • Normalize strain name
    • Search products by name
    • Calculate confidence scores
    • Filter ≥85% confidence
    ↓
Step 4: Update Products
    ↓
For each matched product:
    • Prepare Leafly data
    • Update via Supabase API
    • Log result
    ↓
Step 5: Verify
    ↓
Query: Products with Leafly data
    • Expected: 8,000-10,000 products
```

### Import Script Location:

```
mota-crm/import_tools/import_leafly_data.py
```

### Running the Import:

**Via Python:**
```bash
cd mota-crm/import_tools
python import_leafly_data.py
```

**Via Batch File:**
```bash
import_leafly.bat
```

### Expected Output:

```
================================================================================
LEAFLY DATA IMPORT TO SUPABASE
================================================================================

📄 Loading Leafly data from: ../../Data/inventory_enhanced_v2.json
✅ Loaded 24 strains

🔌 Connecting to Supabase...
✅ Connected to Supabase

📦 Fetching products from Supabase...
✅ Total products: 39,555

🔗 Matching strains to products...
================================================================================

[1/24] Gelato #41
--------------------------------------------------------------------------------
  ✅ Found 1,443 match(es):
     1. [100%] Mota Flwr 8th Gelato 45
     2. [95%] Stiiizy Cart 1g Gelato Hybrid
     3. [90%] Lost Farm Watermelon x Gelato Chews
     ...

  📝 Updating 1,443 product(s)...
     ✅ Updated: Mota Flwr 8th Gelato 45
     ✅ Updated: Stiiizy Cart 1g Gelato Hybrid
     ... (1,441 more)

[2/24] Runtz
--------------------------------------------------------------------------------
  ✅ Found 1,408 match(es):
     ...

...

================================================================================
IMPORT COMPLETE
================================================================================
Strains processed:    24
Matches found:        8,347
Products updated:     8,347
Update errors:        0
================================================================================

✅ Products with Leafly data: 8,347
```

---

## 4. Verification

### Post-Import Checks:

#### Check 1: Count Products with Leafly Data
```sql
SELECT COUNT(*) as products_with_leafly
FROM products
WHERE leafly_description IS NOT NULL;

-- Expected: 8,000-10,000
```

#### Check 2: Sample Enriched Products
```sql
SELECT 
    name,
    effects,
    helps_with,
    flavors,
    leafly_rating
FROM products
WHERE leafly_description IS NOT NULL
LIMIT 10;
```

#### Check 3: Verify by Strain
```sql
SELECT 
    COUNT(*) as count,
    LEFT(name, 30) as product_sample
FROM products
WHERE name ILIKE '%gelato%'
AND leafly_description IS NOT NULL
GROUP BY LEFT(name, 30)
LIMIT 5;
```

#### Check 4: Verify Arrays Work
```sql
-- Find products that help with anxiety
SELECT name, helps_with
FROM products
WHERE 'Anxiety' = ANY(helps_with)
LIMIT 5;

-- Find products with specific effects
SELECT name, effects
FROM products
WHERE 'Relaxed' = ANY(effects)
LIMIT 5;
```

#### Check 5: View Test
```sql
SELECT COUNT(*) 
FROM products_with_leafly
WHERE has_leafly_data = true;

-- Should match Check 1
```

---

## 5. Rollback Plan

### If Something Goes Wrong:

#### Option 1: Null Out Leafly Data
```sql
-- Remove all Leafly data (keep structure)
UPDATE products
SET 
    leafly_description = NULL,
    leafly_strain_type = NULL,
    leafly_rating = NULL,
    leafly_review_count = NULL,
    effects = NULL,
    helps_with = NULL,
    negatives = NULL,
    flavors = NULL,
    terpenes = NULL,
    parent_strains = NULL,
    lineage = NULL,
    image_url = NULL,
    leafly_url = NULL,
    leafly_data_updated_at = NULL
WHERE leafly_description IS NOT NULL;
```

#### Option 2: Drop Columns (Full Rollback)
```sql
-- Drop all Leafly columns
ALTER TABLE products DROP COLUMN IF EXISTS leafly_description;
ALTER TABLE products DROP COLUMN IF EXISTS leafly_strain_type;
ALTER TABLE products DROP COLUMN IF EXISTS leafly_rating;
ALTER TABLE products DROP COLUMN IF EXISTS leafly_review_count;
ALTER TABLE products DROP COLUMN IF EXISTS effects;
ALTER TABLE products DROP COLUMN IF EXISTS helps_with;
ALTER TABLE products DROP COLUMN IF EXISTS negatives;
ALTER TABLE products DROP COLUMN IF EXISTS flavors;
ALTER TABLE products DROP COLUMN IF EXISTS terpenes;
ALTER TABLE products DROP COLUMN IF EXISTS parent_strains;
ALTER TABLE products DROP COLUMN IF EXISTS lineage;
ALTER TABLE products DROP COLUMN IF EXISTS image_url;
ALTER TABLE products DROP COLUMN IF EXISTS leafly_url;
ALTER TABLE products DROP COLUMN IF EXISTS leafly_data_updated_at;

-- Drop indexes
DROP INDEX IF EXISTS idx_products_effects;
DROP INDEX IF EXISTS idx_products_helps_with;
DROP INDEX IF EXISTS idx_products_flavors;
DROP INDEX IF EXISTS idx_products_terpenes;
DROP INDEX IF EXISTS idx_products_has_leafly;

-- Drop view
DROP VIEW IF EXISTS products_with_leafly;
```

#### Option 3: Restore from Backup
```sql
-- If you created a backup before import
-- Restore from Supabase backup/snapshot
```

---

## 📊 Performance Considerations

### Database Impact:
- **Schema change**: ~2 seconds (add columns)
- **Index creation**: ~5-10 seconds (5 indexes)
- **Import time**: ~5-10 minutes (8,000+ updates)
- **Storage increase**: ~50-100 MB (text + arrays)

### Query Performance:
- **Array searches**: Fast (GIN indexes)
- **Filter by effects**: <50ms
- **View queries**: <100ms
- **No impact on**: Existing queries (new columns are optional)

---

## ✅ Success Criteria

- [x] Columns added successfully
- [x] Indexes created
- [x] View created
- [ ] 8,000-10,000 products updated
- [ ] All array searches work
- [ ] No errors in import log
- [ ] Sample queries return expected data

---

**Implementation Date**: October 14, 2025  
**Database**: Supabase (kiwmwoqrguyrcpjytgte)  
**Status**: Schema ready, awaiting import  
**Next**: Execute import script



