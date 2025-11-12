# 🔗 Leafly Integration with YOUR Supabase Schema

**Your Question:** "How will we tether this to the other data? Do we need another database?"

**Answer:** NO! Your existing schema is PERFECT. Everything connects through your `products` table via the `sku` field (your inventory codes).

---

## 🗄️ Your Current Schema (Simplified)

```
┌─────────────────────────────────────────────────────────────────┐
│                    YOUR DATABASE SCHEMA                         │
└─────────────────────────────────────────────────────────────────┘

customers                    transactions              transaction_items
┌──────────────┐            ┌──────────────┐          ┌─────────────────┐
│ id           │───────────▶│ customer_id  │          │ transaction_id  │
│ member_id    │            │ transaction_id│─────────▶│ product_sku     │◀─┐
│ phone        │            │ date         │          │ product_name    │  │
│ name         │            │ total_amount │          │ strain          │  │
│ loyalty_pts  │            │ shop_location│          │ quantity        │  │
│ vip_status   │            │ staff_name   │          │ total_price     │  │
└──────────────┘            └──────────────┘          └─────────────────┘  │
                                                                           │
                                                       ┌─────────────────┐  │
                                                       │   products      │  │
                                                       ├─────────────────┤  │
                                                       │ id              │  │
                                                       │ sku             │──┘
                                                       │ name            │
                                                       │ strain          │ ← Match here!
                                                       │ thc_content     │
                                                       │ cbd_content     │
                                                       │ retail_price    │
                                                       │                 │
                                                       │ + LEAFLY DATA ✨│
                                                       └─────────────────┘
                                                              │
                                    ┌──────────────┬──────────┼──────────┬──────────┐
                                    ▼              ▼          ▼          ▼          ▼
                              customer_product_  staff    messages    leads    AI/CRM
                              affinity (via sku)
```

---

## ✅ The Integration (NO New Database Needed!)

### Step 1: Add Leafly Columns to YOUR `products` Table

Your existing `products` table has:
```sql
products (
    id,
    product_id,
    sku,              ← YOUR INVENTORY CODE!
    name,
    brand,
    category,
    strain,           ← MATCH WITH LEAFLY HERE!
    flower_type,
    vendor,
    thc_content,      ← Already have this
    cbd_content,      ← Already have this
    retail_price,
    cost,
    is_active,
    created_at
)
```

**We ADD these columns** (via `01_add_leafly_columns.sql`):
```sql
-- New Leafly columns:
    leafly_strain_type,      -- Hybrid, Indica, Sativa
    leafly_description,      -- Full 335-char description
    leafly_rating,           -- 4.6 stars
    leafly_review_count,     -- 151 reviews
    effects[],               -- ["Relaxed", "Euphoric", "Happy"]
    helps_with[],            -- ["Anxiety", "Stress", "Pain"]
    negatives[],             -- ["Dry mouth", "Dry eyes"]
    flavors[],               -- ["Lavender", "Pepper", "Pine"]
    terpenes[],              -- ["Limonene", "Myrcene"]
    parent_strains[],        -- Parent strain names
    lineage,                 -- "Parent1 x Parent2"
    image_url,               -- Product image
    leafly_url,              -- Link to Leafly
    leafly_data_updated_at   -- Import timestamp
```

**Result:** ONE table with ALL data (yours + Leafly)!

---

## 🔗 How Everything Connects

### Connection 1: **Inventory Codes (`sku`)**

```sql
-- Your inventory code IS the link!
SELECT 
    sku,                    -- YOUR inventory code
    name,
    strain,
    leafly_description,     -- NEW!
    effects,                -- NEW!
    helps_with              -- NEW!
FROM products
WHERE sku = 'YOUR-INVENTORY-CODE';
```

**Example Result:**
```
sku: "MOTA-GELATO41-3.5"
name: "MOTA - Gelato 41 - 3.5g"
strain: "Gelato 41"
leafly_description: "Gelato #41 is a hybrid strain that is high in THC..."
effects: ["Relaxed", "Euphoric", "Happy", "Tingly"]
helps_with: ["Anxiety", "Stress", "Depression", "Pain"]
```

---

### Connection 2: **Transaction Items → Products (via `product_sku`)**

Your `transaction_items` table already has `product_sku` that links to `products.sku`!

```sql
-- What did customer buy? (with Leafly data)
SELECT 
    ti.transaction_id,
    ti.product_sku,         -- YOUR inventory code
    ti.product_name,
    ti.quantity,
    ti.total_price,
    p.leafly_description,   -- From products table!
    p.effects,              -- From products table!
    p.helps_with,           -- From products table!
    p.flavors,              -- From products table!
    p.image_url             -- From products table!
FROM transaction_items ti
JOIN products p ON ti.product_sku = p.sku
WHERE ti.transaction_id = 'TRANS-12345';
```

---

### Connection 3: **Customer Purchase History with Effects**

```sql
-- What effects does this customer like?
SELECT 
    c.name,
    c.phone,
    t.date,
    ti.product_name,
    p.effects,              -- Array of effects
    p.helps_with            -- Medical uses
FROM customers c
JOIN transactions t ON c.id = t.customer_id
JOIN transaction_items ti ON t.transaction_id = ti.transaction_id
JOIN products p ON ti.product_sku = p.sku
WHERE c.phone = '+16199773020'
AND p.effects IS NOT NULL   -- Only products with Leafly data
ORDER BY t.date DESC;
```

**Example Result:**
```
name: "John Smith"
phone: "+16199773020"
date: "2025-10-10"
product_name: "MOTA - Gelato 41 - 3.5g"
effects: ["Relaxed", "Euphoric", "Happy"]
helps_with: ["Anxiety", "Stress", "Depression"]
```

---

### Connection 4: **Customer Product Affinity + Leafly**

Your `customer_product_affinity` table tracks what customers buy repeatedly. Now add Leafly insights!

```sql
-- What effects does this customer buy most often?
SELECT 
    c.name,
    cpa.product_name,
    cpa.purchase_count,     -- How many times bought
    p.effects,              -- What effects they prefer
    p.flavors,              -- What flavors they prefer
    p.helps_with            -- What they use it for
FROM customer_product_affinity cpa
JOIN customers c ON cpa.customer_id = c.id
JOIN products p ON cpa.product_sku = p.sku
WHERE c.phone = '+16199773020'
AND p.effects IS NOT NULL
ORDER BY cpa.purchase_count DESC;
```

**AI Insight:**
> "John Smith prefers Hybrid strains with Relaxed and Euphoric effects. 
> He's purchased Gelato 41 6 times. Consider recommending Ice Cream Cake 
> (similar effects) on his next visit!"

---

## 🤖 AI Queries Using YOUR Schema

### Query 1: "What helps with anxiety?" (Medical Use Case)

```sql
SELECT 
    sku,                    -- YOUR inventory code
    name,
    strain,
    helps_with,
    effects,
    retail_price,
    is_active              -- In stock?
FROM products
WHERE 'Anxiety' = ANY(helps_with)
AND is_active = true       -- Only active products
ORDER BY leafly_rating DESC
LIMIT 10;
```

**AI Response:**
> "I have 8 products that help with anxiety:
> 
> 1. **Gelato #41** (SKU: MOTA-GELATO41-3.5) - $40
>    Effects: Relaxed, Euphoric, Happy
> 
> 2. **Ice Cream Cake** (SKU: MOTA-ICC-3.5) - $45
>    Effects: Relaxed, Sleepy, Calm"

---

### Query 2: "Show me products this customer liked before"

```sql
-- Find similar products based on customer's purchase history
WITH customer_effects AS (
    SELECT UNNEST(p.effects) as effect
    FROM customers c
    JOIN transactions t ON c.id = t.customer_id
    JOIN transaction_items ti ON t.transaction_id = ti.transaction_id
    JOIN products p ON ti.product_sku = p.sku
    WHERE c.phone = '+16199773020'
    AND p.effects IS NOT NULL
    GROUP BY effect
    ORDER BY COUNT(*) DESC
    LIMIT 3  -- Top 3 effects
)
SELECT DISTINCT
    p.sku,
    p.name,
    p.effects,
    p.retail_price
FROM products p, customer_effects ce
WHERE ce.effect = ANY(p.effects)
AND p.is_active = true
AND p.sku NOT IN (
    -- Exclude already purchased
    SELECT ti.product_sku
    FROM customers c
    JOIN transactions t ON c.id = t.customer_id
    JOIN transaction_items ti ON t.transaction_id = ti.transaction_id
    WHERE c.phone = '+16199773020'
)
LIMIT 5;
```

---

### Query 3: "Find products by inventory code with full details"

```sql
-- Super simple lookup by YOUR inventory code
SELECT 
    sku,                    -- YOUR inventory code
    name,
    strain,
    thc_content,
    cbd_content,
    retail_price,
    leafly_description,     -- Full description
    effects,                -- All effects
    helps_with,             -- Medical uses
    flavors,                -- Flavor profile
    terpenes,               -- Terpene profile
    parent_strains,         -- Genetics
    lineage,                -- Lineage
    image_url,              -- Image
    leafly_rating,          -- Rating
    leafly_review_count     -- Review count
FROM products
WHERE sku = 'MOTA-GELATO41-3.5';
```

**Perfect for:**
- CRM viewers (display full product card)
- AI product descriptions
- Customer-facing apps
- POS system integration

---

## 📊 Your Complete Data Flow (After Integration)

```
┌─────────────────────────────────────────────────────────────────┐
│                     FULL DATA FLOW                              │
└─────────────────────────────────────────────────────────────────┘

1. Customer texts: "+16199773020"
      ↓
2. Lookup: customers.phone → customer.id
      ↓
3. Get history: transactions WHERE customer_id = customer.id
      ↓
4. Get items: transaction_items WHERE transaction_id = transaction.id
      ↓
5. Get product details: products WHERE sku = transaction_items.product_sku
      ↓
6. NOW YOU HAVE:
   ✓ Customer info (name, loyalty points, VIP status)
   ✓ Purchase history (dates, amounts, staff)
   ✓ Products bought (names, quantities, prices)
   ✓ Product details (THC, CBD, retail price)
   ✓ LEAFLY DATA (descriptions, effects, flavors, images!) ✨
      ↓
7. AI/CRM uses this to:
   - Recommend similar products (by effects)
   - Answer "what helps with anxiety?"
   - Show product images
   - Personalize recommendations
   - Track preferences (effects, flavors, terpenes)
```

---

## 🎯 Real-World Example

### Scenario: Customer calls asking about a product

**Step 1: Lookup by inventory code (SKU)**
```sql
SELECT * FROM products WHERE sku = 'MOTA-GELATO41-3.5';
```

**Step 2: Staff sees enriched product card:**
```
┌────────────────────────────────────────────────────┐
│ 🌿 Gelato #41              ⭐ 4.6 (151 reviews)    │
│ Hybrid Strain                                      │
│                                                    │
│ SKU: MOTA-GELATO41-3.5     [Product Image]        │
│                                                    │
│ 💊 THC: 21% | CBD: <1%                            │
│ 💰 Price: $40.00 | 📦 In Stock                    │
│                                                    │
│ 🎯 Effects:                                        │
│    Relaxed • Euphoric • Happy • Tingly            │
│                                                    │
│ 💚 Helps With:                                     │
│    Anxiety • Stress • Depression • Pain           │
│                                                    │
│ 🍇 Flavors:                                        │
│    Lavender • Pepper • Earthy • Pine              │
│                                                    │
│ 🧬 Lineage:                                        │
│    Sunset Sherbert × Thin Mint Cookies            │
│                                                    │
│ [View on Leafly] [Add to Cart]                    │
└────────────────────────────────────────────────────┘
```

**Step 3: Check if customer bought it before:**
```sql
SELECT t.date, ti.quantity
FROM customers c
JOIN transactions t ON c.id = t.customer_id
JOIN transaction_items ti ON t.transaction_id = ti.transaction_id
WHERE c.phone = '+16199773020'
AND ti.product_sku = 'MOTA-GELATO41-3.5'
ORDER BY t.date DESC;
```

**Step 4: Suggest similar products:**
```sql
SELECT name, sku, effects, retail_price
FROM products
WHERE effects && ARRAY['Relaxed', 'Euphoric']  -- Similar effects
AND sku != 'MOTA-GELATO41-3.5'                -- Not the same product
AND is_active = true
LIMIT 3;
```

---

## ✅ Summary: How It All "Tethers"

### 1. **ONE Database** ✓
   - Your Supabase database
   - No new database needed
   - All tables stay as-is

### 2. **ONE Table Enhanced** ✓
   - `products` table gets Leafly columns
   - All other tables link via existing relationships

### 3. **ONE Key Field** ✓
   - `sku` is your inventory code
   - Everything links through `product_sku` → `sku`

### 4. **ONE View for Easy Access** ✓
   - `products_with_leafly` view
   - Combines all data in one place
   - Simple queries for AI/CRM

### 5. **ALL Connections Work** ✓
   - customers → transactions → transaction_items → products ✓
   - customer_product_affinity → products ✓
   - Everything gets Leafly data automatically ✓

---

## 🚀 Next Steps

1. **Run SQL migration** (adds columns to your `products` table)
2. **Run import script** (matches strains, updates products)
3. **Query via `sku`** (your inventory codes now have Leafly data!)
4. **Use in AI/CRM** (all the new fields are accessible)

**No schema changes needed to other tables!**  
**No new database needed!**  
**Everything connects through existing `sku` relationships!** ✅

---

**Status**: Your schema is PERFECT for this integration! 🎉  
**Action**: Just run the SQL + import script, and you're done!




