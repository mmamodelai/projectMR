# 🌿 Leafly Data Import - Quick Reference

## 📍 Purpose
Import rich Leafly strain data (24 strains) into your Supabase products table to enable:
- AI-powered product recommendations
- Medical use case filtering
- Flavor & effects-based search
- Enhanced CRM product cards

---

## ⚡ Quick Start (15 Minutes)

### Step 1: Add Columns to Products Table (5 min)

1. Open **Supabase SQL Editor**
2. Copy entire contents of: `01_add_leafly_columns.sql`
3. Paste and click **RUN**
4. Verify: You should see "LEAFLY COLUMNS ADDED SUCCESSFULLY"

**What it does:**
- Adds 14 new columns to products table
- Creates GIN indexes for fast array searches
- Creates `products_with_leafly` view

---

### Step 2: Update API Key (2 min)

1. Open: `import_leafly_data.py`
2. Find line 24: `SUPABASE_KEY = 'your-service-role-key-here'`
3. Replace with your actual Supabase **service_role** key

**Where to get the key:**
- Go to: Supabase Dashboard
- Navigate to: Project Settings → API
- Copy: `service_role` key (starts with `eyJ...`)
- ⚠️ **Important**: Use service_role, NOT anon key!

---

### Step 3: Run Import (5 min)

**Option A: Batch File (Easy)**
```bash
# Double-click:
import_leafly.bat
```

**Option B: Command Line**
```bash
# From mota-crm/import_tools/ folder:
python import_leafly_data.py
```

**What it does:**
- Loads: `../../Data/inventory_enhanced_v2.json` (24 strains)
- Matches strain names with products (fuzzy matching)
- Updates products with Leafly data
- Shows progress and statistics

**Expected output:**
```
================================================================================
LEAFLY DATA IMPORT TO SUPABASE
================================================================================

📄 Loading Leafly data from: ../Data/inventory_enhanced_v2.json
✅ Loaded 24 strains

🔌 Connecting to Supabase...
✅ Connected to Supabase

📦 Fetching products from Supabase...
✅ Total products: 39,555

🔗 Matching strains to products...
================================================================================

[1/24] Gelato #41
--------------------------------------------------------------------------------
  ✅ Found 3 match(es):
     1. [100%] MOTA - Gelato 41 - 3.5g
     2. [95%] Gelato 41 Flower
     3. [90%] Premium Gelato #41

  📝 Updating 3 product(s)...
     ✅ Updated: MOTA - Gelato 41 - 3.5g
     ✅ Updated: Gelato 41 Flower
     ✅ Updated: Premium Gelato #41

...

================================================================================
IMPORT COMPLETE
================================================================================
Strains processed:    24
Matches found:        72
Products updated:     68
Update errors:        0
================================================================================
```

---

### Step 4: Verify (3 min)

**Option 1: SQL Query**
```sql
-- In Supabase SQL Editor:
SELECT 
    COUNT(*) as total_products,
    COUNT(leafly_description) as products_with_leafly
FROM products;
```

**Expected result:**
- `total_products`: 39,555 (or your total)
- `products_with_leafly`: 50-100 (matched products)

**Option 2: View Sample Data**
```sql
SELECT 
    name, 
    leafly_strain_type, 
    effects, 
    helps_with, 
    flavors
FROM products_with_leafly
WHERE leafly_description IS NOT NULL
LIMIT 5;
```

---

## 📊 What Gets Imported

### For Each Matched Product:

| Column | Example | Type |
|--------|---------|------|
| `leafly_strain_type` | "Hybrid" | TEXT |
| `leafly_description` | "Gelato #41 is a hybrid strain that is high in THC..." | TEXT |
| `leafly_rating` | 4.62 | DECIMAL |
| `leafly_review_count` | 151 | INTEGER |
| `effects` | ["Relaxed", "Euphoric", "Happy"] | TEXT[] |
| `helps_with` | ["Anxiety", "Stress", "Depression"] | TEXT[] |
| `negatives` | ["Dry mouth", "Dry eyes"] | TEXT[] |
| `flavors` | ["Lavender", "Pepper", "Flowery"] | TEXT[] |
| `terpenes` | ["Caryophyllene", "Limonene"] | TEXT[] |
| `parent_strains` | ["Sunset Sherbert", "Thin Mint Cookies"] | TEXT[] |
| `lineage` | "Sunset Sherbert x Thin Mint Cookies" | TEXT |
| `image_url` | "https://images.leafly.com/..." | TEXT |
| `leafly_url` | "https://www.leafly.com/strains/..." | TEXT |
| `leafly_data_updated_at` | "2025-10-13T20:45:30" | TIMESTAMPTZ |

---

## 🤖 Using the Data (AI Queries)

### Find Products by Effect
```sql
SELECT name, effects, retail_price
FROM products_with_leafly
WHERE 'Relaxed' = ANY(effects)
AND is_in_stock = true
ORDER BY leafly_rating DESC
LIMIT 10;
```

### Find Products for Medical Use
```sql
SELECT name, helps_with, leafly_description
FROM products_with_leafly
WHERE 'Anxiety' = ANY(helps_with)
AND is_in_stock = true;
```

### Find Products by Flavor
```sql
SELECT name, flavors, terpenes
FROM products_with_leafly
WHERE 'Citrus' = ANY(flavors)
OR 'Lemon' = ANY(flavors);
```

### Get Full Product Profile
```sql
SELECT *
FROM products_with_leafly
WHERE name LIKE '%Gelato%41%';
```

---

## 🔧 Troubleshooting

### Error: "Cannot find path to JSON file"
**Solution**: Make sure you're running from `mota-crm/import_tools/` folder
```bash
cd mota-crm/import_tools
python import_leafly_data.py
```

### Error: "Please update SUPABASE_KEY"
**Solution**: Edit `import_leafly_data.py` line 24 with your actual key

### Error: "Missing dependencies"
**Solution**: Install required packages
```bash
pip install supabase fuzzywuzzy python-levenshtein
```

### Few or No Matches Found
**Possible causes:**
- Product names in database don't match strain names
- Strain names include extra words (brand, quantity, etc.)
- Fuzzy matching threshold too high (85%)

**Solution**: Check the matching output, look for patterns in product names

### Import Runs but No Data Updates
**Check:**
1. Service role key (not anon key)
2. Products table exists
3. Columns were added successfully
4. No permission errors in script output

---

## 📁 Files in This Folder

### Core Files:
- `01_add_leafly_columns.sql` - SQL migration to add columns
- `import_leafly_data.py` - Main import script
- `import_leafly.bat` - Windows launcher
- `README_LEAFLY_IMPORT.md` - This file

### Related Documentation:
- `../docs/LEAFLY_INTEGRATION_STRATEGY.md` - Full strategy doc
- `../docs/LEAFLY_INTEGRATION_VISUAL.md` - Visual guide with examples

### Data Source:
- `../../Data/inventory_enhanced_v2.json` - 24 Leafly strains

---

## ✅ Success Checklist

After import, you should have:
- [x] New columns in products table
- [x] GIN indexes created
- [x] products_with_leafly view created
- [x] 50-100 products updated with Leafly data
- [x] All matched products have descriptions
- [x] Effects, flavors, terpenes populated
- [x] Image URLs available

---

## 🚀 Next Steps

### For MotaBot AI:
1. Update AI prompts to query `products_with_leafly` view
2. Enable effect-based recommendations
3. Add medical use case filtering
4. Implement flavor preferences

### For CRM Viewers:
1. Add Leafly data to product detail cards
2. Display strain effects and flavors
3. Show ratings and review counts
4. Include product images

### For Customer App:
1. Create visual product cards with images
2. Add "Helps with" badges
3. Show flavor profiles
4. Display strain lineage

---

**Status**: Ready to use  
**Time Required**: 15 minutes  
**Difficulty**: Easy (copy/paste + run)  
**Value**: Huge! 🎉

**Questions?** See full docs in `../docs/LEAFLY_INTEGRATION_*.md`



