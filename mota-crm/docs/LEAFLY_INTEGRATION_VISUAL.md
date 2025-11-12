# 🌿 Leafly Integration - Visual Guide

## 📊 The Big Picture

```
┌─────────────────────────────────────────────────────────────────┐
│                    LEAFLY DATA FLOW                             │
└─────────────────────────────────────────────────────────────────┘

Data/inventory_enhanced_v2.json (24 strains)
         │
         │ Leafly Scraper Output
         ▼
┌────────────────────────┐
│  LEAFLY JSON DATA      │
│                        │
│  • Gelato #41          │
│  • Ice Cream Cake      │
│  • Green Crack         │
│  • 21 more strains...  │
└────────────────────────┘
         │
         │ import_leafly_data.py
         │ (Matches strain names)
         ▼
┌─────────────────────────────────────────────────────────────────┐
│              SUPABASE PRODUCTS TABLE (Enhanced)                 │
│                                                                 │
│  BEFORE                           AFTER                         │
│  ─────────────────────────────────────────────────────────────  │
│  • name                           • name                        │
│  • category                       • category                    │
│  • thc_percent                    • thc_percent                 │
│  • cbd_percent                    • cbd_percent                 │
│                                   • leafly_description ✨       │
│                                   • effects[] ✨                │
│                                   • helps_with[] ✨             │
│                                   • flavors[] ✨                │
│                                   • terpenes[] ✨               │
│                                   • parent_strains[] ✨         │
│                                   • lineage ✨                  │
│                                   • image_url ✨                │
└─────────────────────────────────────────────────────────────────┘
         │
         ├──────────────────┬──────────────────┬─────────────────┐
         ▼                  ▼                  ▼                 ▼
  Transaction Items    AI (MotaBot)      CRM Viewers      Customer App
  (product_id)         Recommendations    Product Cards    Visual Display
```

---

## 🔗 Data Relationships

### How Everything Links Together:

```
CUSTOMERS                TRANSACTIONS              TRANSACTION_ITEMS
┌─────────────┐         ┌─────────────┐          ┌─────────────────┐
│ member_id   │────────▶│ customer_id │          │ transaction_id  │
│ name        │         │ trans_id    │─────────▶│ product_id      │
│ phone       │         │ date        │          │ product_name    │
│ vip_status  │         │ total_amt   │          │ category        │
└─────────────┘         └─────────────┘          └─────────────────┘
                                                          │
                                                          │ Links via
                                                          │ product_id
                                                          ▼
                                            ┌───────────────────────────┐
                                            │  PRODUCTS (with Leafly)   │
                                            ├───────────────────────────┤
                                            │ product_id                │
                                            │ name                      │
                                            │ leafly_description ✨     │
                                            │ effects[] ✨              │
                                            │ helps_with[] ✨           │
                                            │ flavors[] ✨              │
                                            │ terpenes[] ✨             │
                                            │ lineage ✨                │
                                            │ image_url ✨              │
                                            └───────────────────────────┘
```

---

## 🤖 AI Query Examples

### Scenario 1: Customer Asks "What helps with anxiety?"

```
Customer: "What do you have that helps with anxiety?"
    ↓
AI Query:
    SELECT name, leafly_description, helps_with, effects, retail_price
    FROM products_with_leafly
    WHERE 'Anxiety' = ANY(helps_with)
    AND is_in_stock = true
    AND category LIKE '%Flower%'
    ORDER BY leafly_rating DESC
    LIMIT 5;
    ↓
AI Response:
    "I have several great options for anxiety:
    
    1. **Gelato #41** ($40) - Hybrid strain
       Effects: Relaxed, Euphoric, Happy
       Great for: Anxiety, Stress, Depression
       
    2. **Ice Cream Cake** ($45) - Indica
       Effects: Relaxed, Sleepy, Calm
       Perfect for: Anxiety, Pain, Insomnia
    
    Would you like to know more about either of these?"
```

### Scenario 2: Customer Asks About a Specific Product

```
Customer: "Tell me about Gelato 41"
    ↓
AI Query:
    SELECT *
    FROM products_with_leafly
    WHERE name LIKE '%Gelato%41%'
    LIMIT 1;
    ↓
AI Response:
    "**Gelato #41** is a fantastic Hybrid strain!
    
    🌿 Effects: Relaxed, Aroused, Tingly, Euphoric, Happy
    💊 Helps With: Anxiety, Stress, Depression, Pain, Insomnia
    🍇 Flavors: Lavender, Pepper, Flowery, Earthy, Pine
    🧬 Terpenes: Caryophyllene, Limonene, Myrcene
    👨‍👩‍👧 Parents: Sunset Sherbert x Thin Mint Cookies
    
    Description: Gelato #41 is a hybrid strain that is high in THC and 
    offers a heavy, relaxing body high without clouding the mind...
    
    ⭐ Rating: 4.6/5 (275 reviews on Leafly)
    💰 Price: $40.00
    📦 In Stock: Yes
    
    Would you like to add this to your order?"
```

### Scenario 3: Find Similar Products

```
Customer: "Do you have anything like Ice Cream Cake?"
    ↓
AI Query:
    -- First, get Ice Cream Cake's profile
    SELECT effects, helps_with, strain_type
    FROM products_with_leafly
    WHERE name LIKE '%Ice Cream Cake%';
    
    -- Then find similar products
    SELECT name, effects, helps_with, parent_strains
    FROM products_with_leafly
    WHERE strain_type = 'Indica'
    AND effects && ARRAY['Relaxed', 'Sleepy', 'Calm']
    AND name NOT LIKE '%Ice Cream Cake%'
    AND is_in_stock = true
    LIMIT 3;
    ↓
AI Response:
    "Sure! Since you like Ice Cream Cake (Indica, Relaxing), 
    you might also enjoy:
    
    1. **Purple Punch** - Similar relaxing Indica effects
       Helps with: Stress, Insomnia, Pain
       
    2. **Gelato #41** - It's actually a parent of Ice Cream Cake!
       More balanced Hybrid, still very relaxing
    
    Would you like to try one of these?"
```

---

## 📱 CRM Viewer Enhancement

### Before (Basic Product Card):
```
┌──────────────────────────────┐
│ Product: MOTA Gelato 41      │
│                              │
│ Category: Flower             │
│ Price: $40.00                │
│ THC: 21%                     │
│ In Stock: Yes                │
└──────────────────────────────┘
```

### After (Enhanced with Leafly):
```
┌────────────────────────────────────────────────┐
│ 🌿 Gelato #41              ⭐ 4.6 (275 reviews)│
│ Hybrid Strain                                  │
│                                                │
│ [Product Image]                                │
│                                                │
│ 💊 THC: 21% | CBD: <1%                        │
│ 💰 Price: $40.00 | 📦 In Stock                │
│                                                │
│ 🎯 Effects:                                    │
│    Relaxed • Euphoric • Happy • Tingly        │
│                                                │
│ 💚 Helps With:                                 │
│    Anxiety • Stress • Depression • Pain       │
│                                                │
│ 🍇 Flavors:                                    │
│    Lavender • Pepper • Earthy • Pine          │
│                                                │
│ 🧬 Lineage:                                    │
│    Sunset Sherbert × Thin Mint Cookies        │
│                                                │
│ 📝 Description:                                │
│ Gelato #41 is a hybrid strain that is high    │
│ in THC and offers a heavy, relaxing body      │
│ high without clouding the mind...             │
│                                                │
│ [View Full Details] [Add to Cart]             │
└────────────────────────────────────────────────┘
```

---

## 📊 Database Schema Visual

### Products Table (Enhanced):

```sql
┌───────────────────────────────────────────────────────────────┐
│                        PRODUCTS                               │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│  EXISTING COLUMNS                                             │
│  ─────────────────────────────────────────────────────────   │
│  id                    SERIAL PRIMARY KEY                     │
│  product_id            TEXT UNIQUE                            │
│  name                  TEXT                                   │
│  category              TEXT                                   │
│  thc_percent           DECIMAL(5,2)                           │
│  cbd_percent           DECIMAL(5,2)                           │
│  retail_price          DECIMAL(10,2)                          │
│  current_stock         INTEGER                                │
│                                                               │
│  NEW LEAFLY COLUMNS ✨                                        │
│  ─────────────────────────────────────────────────────────   │
│  leafly_strain_type    TEXT         -- Hybrid/Indica/Sativa  │
│  leafly_description    TEXT         -- Full 335-char text    │
│  leafly_rating         DECIMAL(3,2) -- 4.6 stars             │
│  leafly_review_count   INTEGER      -- 275 reviews           │
│  effects               TEXT[]       -- ["Relaxed","Happy"]   │
│  helps_with            TEXT[]       -- ["Anxiety","Pain"]    │
│  negatives             TEXT[]       -- ["Dry mouth"]         │
│  flavors               TEXT[]       -- ["Lavender","Pine"]   │
│  terpenes              TEXT[]       -- ["Limonene"]          │
│  parent_strains        TEXT[]       -- Parent strain names   │
│  lineage               TEXT         -- "Parent1 x Parent2"   │
│  image_url             TEXT         -- Leafly image          │
│  leafly_url            TEXT         -- Leafly page link      │
│  leafly_data_updated_at TIMESTAMPTZ -- When data added       │
│                                                               │
└───────────────────────────────────────────────────────────────┘

INDEXES:
  ✓ idx_products_effects (GIN) -- Fast array searches
  ✓ idx_products_helps_with (GIN)
  ✓ idx_products_flavors (GIN)
  ✓ idx_products_terpenes (GIN)
```

---

## 🎯 Use Cases

### 1. Product Recommendations
```
"Show me energizing Sativa strains"
WHERE strain_type = 'Sativa' 
AND 'Energetic' = ANY(effects)
```

### 2. Medical Use Cases
```
"What helps with insomnia?"
WHERE 'Insomnia' = ANY(helps_with)
```

### 3. Flavor Preferences
```
"I like citrus flavors"
WHERE 'Citrus' = ANY(flavors)
```

### 4. Terpene Profiles
```
"High Limonene strains"
WHERE 'Limonene' = ANY(terpenes)
```

### 5. Strain Lineage
```
"Show me all Gelato crosses"
WHERE 'Gelato' = ANY(parent_strains)
```

---

## 📈 Expected Impact

### For Customers:
- ✅ Better product understanding
- ✅ Informed purchase decisions
- ✅ Personalized recommendations
- ✅ Visual product displays

### For Staff:
- ✅ Quick product information
- ✅ Answer customer questions confidently
- ✅ Suggest alternatives easily
- ✅ Upsell with knowledge

### For Business:
- ✅ Competitive advantage (data-driven)
- ✅ Higher customer satisfaction
- ✅ Better inventory positioning
- ✅ Professional image

### For AI (MotaBot):
- ✅ 24 strains with rich data
- ✅ ~50-100 products enhanced (multiple SKUs per strain)
- ✅ 335+ characters of description per strain
- ✅ 14 unique effects to filter by
- ✅ 42 unique flavors for recommendations
- ✅ 8 terpenes for advanced queries
- ✅ Medical use cases for targeted suggestions

---

## 🚀 Quick Start

### 1. Run SQL Migration (5 minutes)
```bash
# In Supabase SQL Editor:
# Copy/paste contents of: 01_add_leafly_columns.sql
# Click "Run"
```

### 2. Update Supabase Key (2 minutes)
```python
# In import_leafly_data.py, line 24:
SUPABASE_KEY = "your-actual-service-role-key"
```

### 3. Run Import (5 minutes)
```bash
# Double-click:
import_leafly.bat

# Or command line:
python import_leafly_data.py
```

### 4. Verify (1 minute)
```sql
-- In Supabase SQL Editor:
SELECT COUNT(*) as products_with_leafly 
FROM products 
WHERE leafly_description IS NOT NULL;
```

### Total Time: ~15 minutes

---

## ✅ Success Criteria

After import, you should have:
- ✅ 24 strains imported from Leafly
- ✅ 50-100 products updated (multiple SKUs per strain)
- ✅ All products have: description, effects, flavors, terpenes
- ✅ AI can query by effects, medical uses, flavors
- ✅ CRM viewers can display rich product cards
- ✅ Image URLs available for visual displays

---

**Status**: Ready to implement  
**Difficulty**: Easy (copy/paste + run)  
**Time**: 15 minutes  
**Value**: Huge! 🚀




