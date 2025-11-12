# 🌿 Leafly Data Integration Strategy

**Purpose**: Integrate rich Leafly strain data into Supabase for enhanced product intelligence  
**Dataset**: 24 strains with comprehensive cannabis information  
**Target**: Link with products, transaction_items, and inventory

---

## 🎯 What We Have

### Leafly Data (Data/inventory_enhanced_v2.json)
```json
{
  "name": "Gelato #41",
  "strain_type": "Hybrid",
  "thc_percent": 21.0,
  "cbd_percent": null,
  "cbg_percent": 1.0,
  "rating": 4.567,
  "review_count": 275,
  "effects": ["Relaxed", "Aroused", "Tingly", ...],
  "helps_with": ["Anxiety", "Stress", "Depression", ...],
  "negatives": ["Dry mouth", "Dry eyes", ...],
  "flavors": ["Lavender", "Pepper", "Flowery", ...],
  "terpenes": ["Caryophyllene", "Limonene", "Myrcene", ...],
  "description": "Full description text...",
  "parent_strains": ["Sunset Sherbert", "Thin Mint Cookies"],
  "lineage": "Sunset Sherbert x Thin Mint Cookies",
  "image_url": "https://images.leafly.com/...",
  "scraped_at": "2025-10-13T16:58:33"
}
```

### Existing Supabase Tables
- **products**: 39,555 products with basic info (name, category, THC/CBD)
- **transaction_items**: 57,568 items with product_name, brand, category
- **inventory**: (from PRODUCT_BATCH_EXPORT) 1,690 items with stock levels

---

## 📊 Integration Strategy

### Option 1: Enhance Products Table (RECOMMENDED)
**Add Leafly columns directly to products table**

✅ **Pros**:
- Simple queries (all data in one table)
- Fast lookups
- Easy for AI to access
- No JOINs needed

❌ **Cons**:
- Not all products will have Leafly data (only flower strains)
- Some NULL values for non-flower products

### Option 2: Separate Strains Table
**Create new `strains` table, link via foreign key**

✅ **Pros**:
- Clean separation (only flower strains)
- No NULL values
- Can be reused across multiple products

❌ **Cons**:
- Requires JOINs for every query
- More complex AI queries
- Extra lookup step

### 🎯 **RECOMMENDATION**: **Option 1** - Add columns to products table

**Why**: Simpler for AI, faster queries, most practical for your use case

---

## 🗄️ Enhanced Products Schema

### Add These Columns to `products` Table:

```sql
-- Leafly Strain Data
ALTER TABLE products ADD COLUMN IF NOT EXISTS leafly_strain_type TEXT; -- Hybrid, Indica, Sativa
ALTER TABLE products ADD COLUMN IF NOT EXISTS leafly_description TEXT;
ALTER TABLE products ADD COLUMN IF NOT EXISTS leafly_rating DECIMAL(3, 2);
ALTER TABLE products ADD COLUMN IF NOT EXISTS leafly_review_count INTEGER;

-- Effects & Benefits (stored as arrays)
ALTER TABLE products ADD COLUMN IF NOT EXISTS effects TEXT[];
ALTER TABLE products ADD COLUMN IF NOT EXISTS helps_with TEXT[];
ALTER TABLE products ADD COLUMN IF NOT EXISTS negatives TEXT[];
ALTER TABLE products ADD COLUMN IF NOT EXISTS flavors TEXT[];
ALTER TABLE products ADD COLUMN IF NOT EXISTS terpenes TEXT[];

-- Lineage
ALTER TABLE products ADD COLUMN IF NOT EXISTS parent_strains TEXT[];
ALTER TABLE products ADD COLUMN IF NOT EXISTS lineage TEXT;

-- Media
ALTER TABLE products ADD COLUMN IF NOT EXISTS image_url TEXT;
ALTER TABLE products ADD COLUMN IF NOT EXISTS leafly_url TEXT;

-- Metadata
ALTER TABLE products ADD COLUMN IF NOT EXISTS leafly_data_updated_at TIMESTAMPTZ;
```

### Why Arrays?
PostgreSQL supports array columns - perfect for lists like effects, flavors, terpenes!

```sql
-- Query examples:
SELECT * FROM products WHERE 'Relaxed' = ANY(effects);
SELECT * FROM products WHERE effects && ARRAY['Relaxed', 'Euphoric'];
```

---

## 🔗 Matching Strategy

### Challenge: Match Leafly Strain Names with Product Names

**Leafly names**: "Gelato #41", "Ice Cream Cake", "Green Crack"  
**Product names**: "MOTA - Gelato 41 - 3.5g", "Ice Cream Cake Flower", "Green Crack (Sativa)"

### Matching Algorithm:

```python
def normalize_strain_name(name):
    """Normalize strain name for matching"""
    name = name.lower().strip()
    # Remove common words
    name = re.sub(r'\b(flower|strain|cannabis|weed|gram|g|oz)\b', '', name)
    # Remove numbers like 3.5g, 1oz
    name = re.sub(r'\d+\.?\d*\s*(g|gram|oz|ounce)', '', name)
    # Remove brand names
    name = re.sub(r'\b(mota|brand|premium)\b', '', name)
    # Normalize #
    name = name.replace('#', '').replace('  ', ' ')
    return name.strip()

# Example:
# "MOTA - Gelato #41 - 3.5g" -> "gelato 41"
# "Ice Cream Cake Flower" -> "ice cream cake"
```

### Matching Approach:

1. **Exact Match**: `normalized_product_name == normalized_strain_name`
2. **Contains Match**: `normalized_strain_name in normalized_product_name`
3. **Fuzzy Match**: Use fuzzy string matching (95% similarity threshold)
4. **Manual Override**: CSV file with product_id → strain_name mappings

---

## 🚀 Implementation Steps

### Step 1: Add Columns to Products Table

```sql
-- Run this migration in Supabase SQL Editor
BEGIN;

-- Basic Leafly fields
ALTER TABLE products ADD COLUMN IF NOT EXISTS leafly_strain_type TEXT;
ALTER TABLE products ADD COLUMN IF NOT EXISTS leafly_description TEXT;
ALTER TABLE products ADD COLUMN IF NOT EXISTS leafly_rating DECIMAL(3, 2);
ALTER TABLE products ADD COLUMN IF NOT EXISTS leafly_review_count INTEGER;

-- Arrays for multi-value fields
ALTER TABLE products ADD COLUMN IF NOT EXISTS effects TEXT[];
ALTER TABLE products ADD COLUMN IF NOT EXISTS helps_with TEXT[];
ALTER TABLE products ADD COLUMN IF NOT EXISTS negatives TEXT[];
ALTER TABLE products ADD COLUMN IF NOT EXISTS flavors TEXT[];
ALTER TABLE products ADD COLUMN IF NOT EXISTS terpenes TEXT[];

-- Lineage
ALTER TABLE products ADD COLUMN IF NOT EXISTS parent_strains TEXT[];
ALTER TABLE products ADD COLUMN IF NOT EXISTS lineage TEXT;

-- Media
ALTER TABLE products ADD COLUMN IF NOT EXISTS image_url TEXT;
ALTER TABLE products ADD COLUMN IF NOT EXISTS leafly_url TEXT;

-- Metadata
ALTER TABLE products ADD COLUMN IF NOT EXISTS leafly_data_updated_at TIMESTAMPTZ;

-- Create indexes for array searches
CREATE INDEX IF NOT EXISTS idx_products_effects ON products USING GIN(effects);
CREATE INDEX IF NOT EXISTS idx_products_helps_with ON products USING GIN(helps_with);
CREATE INDEX IF NOT EXISTS idx_products_flavors ON products USING GIN(flavors);
CREATE INDEX IF NOT EXISTS idx_products_terpenes ON products USING GIN(terpenes);

COMMIT;
```

### Step 2: Import Leafly Data (Python Script)

**Create**: `mota-crm/import_tools/import_leafly_data.py`

```python
#!/usr/bin/env python3
"""
Import Leafly strain data into Supabase products table
Matches strain names with products and updates with rich data
"""

import json
import re
from supabase import create_client
from fuzzywuzzy import fuzz

# Supabase connection
SUPABASE_URL = "your-project-url"
SUPABASE_KEY = "your-service-key"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def normalize_strain_name(name):
    """Normalize strain name for matching"""
    if not name:
        return ""
    
    name = str(name).lower().strip()
    # Remove common words
    name = re.sub(r'\b(flower|strain|cannabis|weed|gram|g|oz|ounce)\b', '', name)
    # Remove quantities
    name = re.sub(r'\d+\.?\d*\s*(g|gram|oz|ounce|mg)', '', name)
    # Remove brand names
    name = re.sub(r'\b(mota|brand|premium)\b', '', name)
    # Normalize special chars
    name = name.replace('#', '').replace('-', ' ').replace('_', ' ')
    # Remove multiple spaces
    name = re.sub(r'\s+', ' ', name)
    return name.strip()

def match_strain_to_products(strain_name, products):
    """Match strain name to products using fuzzy matching"""
    matches = []
    normalized_strain = normalize_strain_name(strain_name)
    
    for product in products:
        product_name = product.get('name', '')
        normalized_product = normalize_strain_name(product_name)
        
        # Exact match
        if normalized_strain == normalized_product:
            matches.append((product, 100))
            continue
        
        # Contains match
        if normalized_strain in normalized_product:
            matches.append((product, 90))
            continue
        
        # Fuzzy match
        similarity = fuzz.ratio(normalized_strain, normalized_product)
        if similarity >= 85:
            matches.append((product, similarity))
    
    # Return best matches
    matches.sort(key=lambda x: x[1], reverse=True)
    return matches

def import_leafly_data(leafly_json_path):
    """Import Leafly data and update products"""
    
    # Load Leafly data
    print("Loading Leafly data...")
    with open(leafly_json_path, 'r', encoding='utf-8') as f:
        leafly_data = json.load(f)
    
    print(f"Loaded {len(leafly_data)} strains")
    
    # Get all products from Supabase
    print("\nFetching products from Supabase...")
    products = []
    page_size = 1000
    offset = 0
    
    while True:
        response = supabase.table('products').select('*').range(offset, offset + page_size - 1).execute()
        if not response.data:
            break
        products.extend(response.data)
        offset += page_size
        print(f"  Fetched {len(products)} products...")
    
    print(f"Total products: {len(products)}")
    
    # Match and update
    matched_count = 0
    updated_count = 0
    
    for strain in leafly_data:
        strain_name = strain['name']
        print(f"\nProcessing: {strain_name}")
        
        # Find matching products
        matches = match_strain_to_products(strain_name, products)
        
        if not matches:
            print(f"  ❌ No matches found")
            continue
        
        # Show matches
        print(f"  ✅ Found {len(matches)} matches:")
        for product, similarity in matches[:3]:  # Show top 3
            print(f"     {similarity}% - {product['name']}")
        
        # Update all high-confidence matches (>85% similarity)
        high_confidence = [m for m in matches if m[1] >= 85]
        
        for product, similarity in high_confidence:
            # Prepare update data
            update_data = {
                'leafly_strain_type': strain.get('strain_type'),
                'leafly_description': strain.get('description'),
                'leafly_rating': float(strain.get('rating', 0)) if strain.get('rating') else None,
                'leafly_review_count': strain.get('review_count', 0),
                'effects': strain.get('effects', []),
                'helps_with': strain.get('helps_with', []),
                'negatives': strain.get('negatives', []),
                'flavors': strain.get('flavors', []),
                'terpenes': strain.get('terpenes', []),
                'parent_strains': strain.get('parent_strains', []),
                'lineage': strain.get('lineage'),
                'image_url': strain.get('image_url'),
                'leafly_url': strain.get('url'),
                'leafly_data_updated_at': 'now()'
            }
            
            # Update product
            try:
                supabase.table('products').update(update_data).eq('id', product['id']).execute()
                updated_count += 1
                print(f"     ✅ Updated: {product['name']}")
            except Exception as e:
                print(f"     ❌ Error updating: {e}")
        
        matched_count += len(high_confidence)
    
    # Summary
    print("\n" + "="*60)
    print("IMPORT COMPLETE")
    print("="*60)
    print(f"Strains processed: {len(leafly_data)}")
    print(f"Product matches found: {matched_count}")
    print(f"Products updated: {updated_count}")
    print("="*60)

if __name__ == "__main__":
    import_leafly_data('../Data/inventory_enhanced_v2.json')
```

### Step 3: Create Helper View for AI

```sql
-- Create a view that combines product data with Leafly info
CREATE OR REPLACE VIEW products_with_leafly AS
SELECT 
    p.id,
    p.product_id,
    p.name,
    p.brand,
    p.category,
    p.strain,
    
    -- Cannabis Profile
    p.flower_type,
    p.thc_percent,
    p.cbd_percent,
    COALESCE(p.leafly_strain_type, p.flower_type) as strain_type,
    
    -- Leafly Data
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
    
    -- Stock & Pricing
    p.retail_price,
    p.current_stock,
    p.is_in_stock,
    
    -- Flags
    CASE 
        WHEN p.leafly_description IS NOT NULL THEN true 
        ELSE false 
    END as has_leafly_data
    
FROM products p;
```

---

## 🤖 AI Query Examples

### Get Product with Full Details
```python
# AI can query like this:
result = supabase.table('products_with_leafly')\
    .select('*')\
    .eq('name', 'Gelato 41')\
    .single()\
    .execute()

# Response:
{
    "name": "MOTA - Gelato 41 - 3.5g",
    "strain_type": "Hybrid",
    "thc_percent": 21.0,
    "leafly_description": "Gelato #41 is a hybrid strain...",
    "effects": ["Relaxed", "Aroused", "Tingly", "Euphoric"],
    "helps_with": ["Anxiety", "Stress", "Depression"],
    "flavors": ["Lavender", "Pepper", "Flowery"],
    "terpenes": ["Caryophyllene", "Limonene", "Myrcene"],
    "lineage": "Sunset Sherbert x Thin Mint Cookies"
}
```

### Find Products by Effect
```sql
SELECT name, effects, helps_with, retail_price
FROM products_with_leafly
WHERE 'Relaxed' = ANY(effects)
AND is_in_stock = true
ORDER BY leafly_rating DESC
LIMIT 10;
```

### Find Products for Specific Need
```sql
SELECT name, helps_with, effects, leafly_description
FROM products_with_leafly
WHERE 'Anxiety' = ANY(helps_with)
AND 'Relaxed' = ANY(effects)
AND has_leafly_data = true;
```

---

## 📊 Data Linkage Diagram

```
Leafly Data (JSON)
      ↓
  [Matching Algorithm]
      ↓
Products Table (Enhanced)
      ↓
      ├──→ Transaction Items (product_id)
      ├──→ Customer Purchases (via transactions)
      └──→ Inventory (via product_id)
```

### Full Query Path:
```
Customer asks: "What helps with anxiety?"
      ↓
AI queries: products WHERE 'Anxiety' = ANY(helps_with)
      ↓
Gets: Products with Leafly data
      ↓
Checks: is_in_stock = true
      ↓
Returns: Product recommendations with descriptions
```

---

## ✅ Benefits

### For AI (MotaBot):
- ✅ Rich product descriptions (335+ chars per strain)
- ✅ Medical use cases ("helps with anxiety, pain, insomnia")
- ✅ Effects data ("relaxed, euphoric, happy")
- ✅ Flavor profiles for recommendations
- ✅ Lineage data for "similar strains" suggestions

### For CRM Viewers:
- ✅ Detailed product cards
- ✅ Images for visual display
- ✅ Customer ratings (7,048 reviews for Green Crack!)
- ✅ Terpene profiles for educated customers

### For Business:
- ✅ Better product knowledge
- ✅ Enhanced customer service
- ✅ Data-driven recommendations
- ✅ Competitive advantage

---

## 📝 Implementation Checklist

- [ ] Run migration SQL (add columns to products table)
- [ ] Install dependencies (`pip install fuzzywuzzy python-levenshtein`)
- [ ] Create import_leafly_data.py script
- [ ] Test matching algorithm on sample data
- [ ] Run full import
- [ ] Verify data in Supabase
- [ ] Create products_with_leafly view
- [ ] Test AI queries
- [ ] Update MotaBot prompts to use new data
- [ ] Update CRM viewers to display Leafly data

---

## 🎯 Expected Results

### Data Coverage:
- **24 strains** with full Leafly data
- **~50-100 products** matched and updated (multiple SKUs per strain)
- **100% of matched products** get descriptions, effects, flavors, terpenes

### AI Capabilities (New):
- "Tell me about Gelato 41" → Full description with effects
- "What helps with anxiety?" → Products filtered by medical use
- "Show me relaxing strains" → Products filtered by effects
- "What are the parents of Ice Cream Cake?" → Lineage information

---

**Status**: Ready to implement  
**Estimated Time**: 2-3 hours  
**Dependencies**: Supabase access, fuzzywuzzy library  
**Next Action**: Run migration SQL, create import script



