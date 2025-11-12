# ⚡ Quick Start - Add Leafly Data to Supabase

## 🎯 Goal
Add 24 Leafly strains to your Supabase products table (15 minutes)

---

## ✅ **STEP 1: Add Columns to Supabase (5 minutes)**

### A. Open Supabase SQL Editor
1. Go to: **https://supabase.com/dashboard**
2. Select your project: **kiwmwoqrguyrcpjytgte**
3. Click: **SQL Editor** (left sidebar)
4. Click: **New query**

### B. Copy & Paste SQL
1. Open: `01_add_leafly_columns.sql` (should be open in VS Code)
2. Select ALL (Ctrl+A)
3. Copy (Ctrl+C)
4. Paste into Supabase SQL Editor
5. Click: **RUN** button (bottom right)

### C. Verify Success
You should see:
```
=================================================================
LEAFLY COLUMNS ADDED SUCCESSFULLY
=================================================================
```

**What this does:**
- Adds 14 new columns to your `products` table
- Creates indexes for fast searches
- Creates `products_with_leafly` view

---

## ✅ **STEP 2: Update Import Script (2 minutes)**

### A. Get Your Supabase Service Role Key
1. In Supabase Dashboard, go to: **Settings** → **API**
2. Find: **Service Role** key (secret)
3. Copy the key (starts with `eyJ...`)

### B. Update Python Script
1. Open: `import_leafly_data.py`
2. Find line 24:
   ```python
   SUPABASE_KEY = 'your-service-role-key-here'
   ```
3. Replace with your actual key:
   ```python
   SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
   ```
4. Save the file (Ctrl+S)

---

## ✅ **STEP 3: Run Import (5 minutes)**

### Option A: Double-Click Batch File
1. Navigate to: `mota-crm\import_tools\`
2. Double-click: `import_leafly.bat`
3. Wait for completion

### Option B: Command Line
```bash
cd mota-crm\import_tools
python import_leafly_data.py
```

### What You'll See:
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

[1/24] Glitter Bomb
--------------------------------------------------------------------------------
  ✅ Found 3 match(es):
     1. [100%] MOTA - Glitter Bomb - 3.5g
     2. [95%] Glitter Bomb Flower
     3. [90%] Premium Glitter Bomb

  📝 Updating 3 product(s)...
     ✅ Updated: MOTA - Glitter Bomb - 3.5g
     ✅ Updated: Glitter Bomb Flower
     ✅ Updated: Premium Glitter Bomb

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

## ✅ **STEP 4: Verify (3 minutes)**

### A. Check in Supabase
1. Go to: **Table Editor** → **products**
2. Look for new columns:
   - `leafly_description`
   - `effects`
   - `helps_with`
   - `flavors`
   - `terpenes`

### B. Run Test Query
In SQL Editor:
```sql
-- How many products have Leafly data?
SELECT COUNT(*) as products_with_leafly
FROM products
WHERE leafly_description IS NOT NULL;

-- View sample data
SELECT 
    sku,
    name,
    strain,
    effects,
    helps_with,
    leafly_rating
FROM products
WHERE leafly_description IS NOT NULL
LIMIT 5;
```

**Expected Result:**
- 50-100 products with Leafly data
- All matched products have descriptions, effects, flavors

---

## 🎉 **SUCCESS!**

You now have:
- ✅ 24 Leafly strains integrated
- ✅ Rich product descriptions
- ✅ Effects, flavors, terpenes data
- ✅ Medical use cases (helps_with)
- ✅ Product images
- ✅ Ready for AI queries!

---

## 🤖 **Next: Use the Data**

### Query by Inventory Code (SKU):
```sql
SELECT * FROM products_with_leafly
WHERE sku = 'YOUR-INVENTORY-CODE';
```

### Find Products by Effect:
```sql
SELECT sku, name, effects, retail_price
FROM products_with_leafly
WHERE 'Relaxed' = ANY(effects)
AND is_active = true;
```

### Find Products for Medical Use:
```sql
SELECT sku, name, helps_with, leafly_description
FROM products_with_leafly
WHERE 'Anxiety' = ANY(helps_with)
AND is_active = true;
```

---

## ⚠️ **Troubleshooting**

### Error: "Please update SUPABASE_KEY"
- Make sure you updated line 24 in `import_leafly_data.py`
- Use the **service_role** key, not the **anon** key

### Error: "Cannot find path to JSON file"
- Make sure you're running from `mota-crm/import_tools/` folder
- The script expects: `../../Data/inventory_enhanced_v2.json`

### Few or No Matches Found
- Check your product names in the `products` table
- Make sure `strain` field has strain names
- The script uses fuzzy matching (85% threshold)

### Import Runs but No Data Updates
- Verify you used the **service_role** key
- Check permissions on the products table
- Look for error messages in the script output

---

## 📚 **Full Documentation**

- **Technical Strategy**: `docs/LEAFLY_INTEGRATION_STRATEGY.md`
- **Visual Guide**: `docs/LEAFLY_INTEGRATION_VISUAL.md`
- **Your Schema Guide**: `docs/YOUR_SCHEMA_LEAFLY_INTEGRATION.md`
- **Complete Package**: `../LEAFLY_SUPABASE_INTEGRATION_COMPLETE.md`

---

**Time Required**: 15 minutes total  
**Difficulty**: Easy (copy/paste + run)  
**Value**: Huge! 🚀

**Questions?** See the full documentation in `docs/` folder.



