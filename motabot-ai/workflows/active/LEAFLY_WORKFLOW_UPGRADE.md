# MotaBot Workflow - Leafly Enhancement Guide

## 🎉 What's New

Your MotaBot AI now has access to **11,515 products with rich Leafly data**!

### New File: `supabaseimport_LEAFLY_ENHANCED.json`

This is an enhanced version of your original workflow with:
- ✅ **Conversation history tracking** - AI sees last 10 messages for context (NEW!)
- ✅ **New Supabase Products tool** - queries the products table
- ✅ **Enhanced system prompt** - tells AI about Leafly data and how to search strains
- ✅ **Better strain search** - AI knows how to find OG Kush, Blue Dream, etc.
- ✅ **Product recommendation capabilities** - effects, flavors, medical uses
- ✅ **All original tools** - customers, transactions, budtenders, Gmail

---

## 🆕 What Changed

### 1. Conversation History (NEW!)

**Two new nodes added to workflow:**
- **"Get Conversation History"** - Pulls last 10 messages for this phone number from database
- **"Format Conversation Context"** - Formats messages as conversation history for AI

**What this enables:**
- ✅ AI sees the full conversation context
- ✅ Can reference previous messages ("Tell me more about the first one")
- ✅ Natural follow-up questions work correctly
- ✅ Better customer experience with contextual responses

**Example:**
```
Customer: "What helps with anxiety?"
AI: "Try OG Kush or Northern Lights"
Customer: "Tell me more about the first one"
AI: [Knows "first one" = OG Kush from conversation history]
```

### 2. New Supabase Tool Added

**"Get many rows in Supabase Products"**
- Queries the `products` table by NAME or STRAIN
- Access to 11,515 products with Leafly data
- Can filter by effects, flavors, medical uses, strain type, ratings
- Searches using ILIKE patterns (e.g., '%OG%' finds OG Kush, Fire OG, etc.)

### 3. Enhanced System Prompt

The AI now knows about:
- **Effects**: Relaxed, Euphoric, Creative, Energetic, Happy, Uplifted, Focused, Giggly, Sleepy, etc.
- **Medical Uses**: Anxiety, Pain, Insomnia, Stress, Depression, Inflammation, Migraines, etc.
- **Flavors**: Pine, Citrus, Diesel, Berry, Earthy, Lemon, Grape, Sweet, etc.
- **Terpenes**: Limonene, Myrcene, Caryophyllene, Linalool, Pinene, etc.
- **Strain Types**: Indica, Sativa, Hybrid
- **Ratings & Reviews**: Leafly star ratings and review counts

---

## 💡 New Capabilities

### Customer Asks: "What can you tell me about OG flower?" 🆕

**AI will:**
1. Use "Get many rows in Supabase Products"
2. Search WHERE (strain ILIKE '%OG%' OR name ILIKE '%OG Kush%') AND leafly_description IS NOT NULL
3. Return products with full Leafly data (we have 1,079 OG Kush products!)

**Response Example**:
```
"Hey Stephen! OG Kush (4.28★, 5665 reviews) is a Hybrid strain known for:
Effects: Relaxed, Euphoric, Happy, Uplifted
Helps with: Anxiety, Stress, Pain, Depression
Flavors: Pine, Diesel, Citrus, Lemon
Great for evening relaxation!"
```

---

### Customer Asks: "Show me relaxing strains"

**AI will:**
1. Use "Get many rows in Supabase Products"
2. Filter WHERE 'Relaxed' = ANY(effects) AND leafly_rating IS NOT NULL
3. Return top-rated products sorted by rating

**Response Example**:
```
"Hey Sarah! Here are our top relaxing strains:
1. Bubba Kush (4.3★) - Indica
2. Northern Lights (4.4★) - Indica  
3. Grape Ape (4.3★) - Indica
All great for winding down!"
```

---

### Customer Asks: "What helps with anxiety and sleep?"

**AI will:**
1. Query products WHERE 'Anxiety' = ANY(helps_with) AND 'Insomnia' = ANY(helps_with)
2. Sort by rating
3. Show top recommendations

**Response Example**:
```
"For anxiety and sleep, I recommend:
1. GG4 (4.6★) - Hybrid, 5502 reviews
2. Granddaddy Purple (4.4★) - Indica
3. Northern Lights (4.4★) - Indica
All highly rated for relaxation!"
```

---

### Customer Asks: "I like citrus flavors"

**AI will:**
1. Query WHERE 'Citrus' = ANY(flavors) OR 'Lemon' = ANY(flavors)
2. Show vapes, concentrates, flower with citrus notes

**Response Example**:
```
"Perfect! Check out these citrus-y options:
1. Lemon Haze (4.3★) - Energetic Sativa
2. Sour Diesel (4.3★) - Classic diesel-lemon
3. Tangie (4.4★) - Sweet tangerine flavor
Which category - vapes, flower, or concentrates?"
```

---

### Customer Asks: "Based on what I've bought, what should I try?"

**AI will:**
1. Get their transaction history
2. Look up the products they purchased
3. Analyze common effects/flavors
4. Recommend similar products they haven't tried

**Response Example**:
```
"Based on your past purchases, you love relaxing indicas with earthy flavors. Try these:
1. Master Kush (4.3★) - Similar to your Bubba Kush purchase
2. Skywalker OG (4.5★) - Great for evening relaxation
Both are highly rated with effects you enjoy!"
```

---

## 📋 How AI Uses The Data

### Effects-Based Filtering

```javascript
// Customer: "Show me energetic strains"
SELECT name, category, leafly_rating, effects
FROM products
WHERE 'Energetic' = ANY(effects)
AND leafly_rating > 4.0
ORDER BY leafly_rating DESC
LIMIT 5
```

### Medical Use Matching

```javascript
// Customer: "Help with pain and inflammation"
SELECT name, helps_with, leafly_rating, leafly_review_count
FROM products
WHERE 'Pain' = ANY(helps_with)
AND 'Inflammation' = ANY(helps_with)
ORDER BY leafly_review_count DESC
LIMIT 5
```

### Flavor Preferences

```javascript
// Customer: "Something fruity and sweet"
SELECT name, flavors, category, leafly_rating
FROM products
WHERE ('Berry' = ANY(flavors) OR 'Grape' = ANY(flavors))
AND 'Sweet' = ANY(flavors)
ORDER BY leafly_rating DESC
```

### Strain Type Filtering

```javascript
// Customer: "Show me sativas"
SELECT name, leafly_strain_type, effects, leafly_rating
FROM products
WHERE leafly_strain_type = 'Sativa'
AND leafly_rating > 4.2
ORDER BY leafly_rating DESC
```

---

## 🔧 Installation

### Option 1: Import New Workflow (Recommended)

1. Open n8n
2. Go to Workflows
3. Click "Import from File"
4. Select `supabaseimport_LEAFLY_ENHANCED.json`
5. Verify Supabase credentials are connected
6. Activate the workflow

### Option 2: Update Existing Workflow

1. Open your existing `supabaseimport.json` workflow
2. Add a new **Supabase Tool** node:
   - Name: "Get many rows in Supabase Products"
   - Operation: Get All
   - Table: `products`
   - Description: "Query 11,515 products with Leafly data: effects, medical uses, flavors, terpenes, ratings"
3. Connect it to the "MotaBot AI" node (ai_tool connection)
4. Update the system prompt in "MotaBot AI" node:
   - Copy the enhanced system message from the new workflow
   - Paste it into your existing workflow's system message field
5. Save and activate

---

## 🧪 Testing

### Test 1: Effects Query
**Send SMS**: "Show me relaxing strains"  
**Expected**: AI queries products WHERE 'Relaxed' = ANY(effects), returns top-rated results

### Test 2: Medical Use
**Send SMS**: "What helps with anxiety?"  
**Expected**: AI queries WHERE 'Anxiety' = ANY(helps_with), shows recommendations

### Test 3: Flavor Preference
**Send SMS**: "I like citrus flavors"  
**Expected**: AI queries WHERE 'Citrus' = ANY(flavors), suggests matching products

### Test 4: Personalized Recommendation
**Send SMS**: "Recommend something like what I bought before"  
**Expected**: AI checks transaction history, finds common effects/flavors, suggests similar products

---

## 📊 Data Available

### 14 New Fields Per Product

| Field | Type | Example |
|-------|------|---------|
| `leafly_strain_type` | TEXT | "Hybrid" |
| `leafly_description` | TEXT | "OG Kush, also known as..." |
| `leafly_rating` | NUMERIC | 4.28 |
| `leafly_review_count` | INTEGER | 5665 |
| `effects` | TEXT[] | ["Relaxed", "Euphoric", "Happy"] |
| `helps_with` | TEXT[] | ["Anxiety", "Pain", "Insomnia"] |
| `negatives` | TEXT[] | ["Dry mouth", "Dry eyes"] |
| `flavors` | TEXT[] | ["Pine", "Diesel", "Citrus"] |
| `terpenes` | TEXT[] | ["Limonene", "Myrcene"] |
| `parent_strains` | TEXT[] | ["Chemdawg", "Lemon Thai"] |
| `lineage` | TEXT | "Chemdawg x Lemon Thai x Hindu Kush" |
| `image_url` | TEXT | "https://images.leafly.com/..." |
| `leafly_url` | TEXT | "https://www.leafly.com/strains/og-kush" |
| `leafly_data_updated_at` | TIMESTAMPTZ | "2025-10-14T04:13:19Z" |

### Coverage
- **11,515 products** (29.1% of inventory)
- **57 unique strains** with complete data
- **All categories**: Vapes, Concentrates, Edibles, Flower, PrePacks

---

## 🎯 Best Practices

### DO:
✅ Let AI filter by effects, flavors, and medical uses  
✅ Recommend products based on customer's past purchases  
✅ Sort by rating for quality recommendations  
✅ Combine effects + medical uses for precise matching  
✅ Use leafly_review_count for social proof  

### DON'T:
❌ Make generic recommendations without using Leafly data  
❌ Ignore customer's flavor preferences  
❌ Forget to mention ratings and reviews  
❌ Recommend products without checking their purchase history first  

---

## 🚀 Advanced Use Cases

### 1. Preference Profiling
**Track** what effects/flavors a customer buys most  
**Recommend** new products with similar profiles  
**Learn** their preferences over time

### 2. Discovery Mode
**Customer**: "Surprise me with something new"  
**AI**: Analyzes purchase history → Finds adjacent effects → Recommends highly-rated products they haven't tried

### 3. Activity-Based Recommendations
**Customer**: "What's good for a creative session?"  
**AI**: Queries WHERE 'Creative' = ANY(effects) AND 'Focused' = ANY(effects)

### 4. Medical Wellness
**Customer**: "Help with chronic pain and inflammation"  
**AI**: Filters by medical uses, shows top-rated options, mentions terpenes that help

---

## 📈 Impact

### Before Leafly Integration:
- Generic product recommendations
- No effect/flavor filtering
- Limited personalization
- Basic "here's what you bought" responses

### After Leafly Integration:
- **Smart filtering** by 13+ effects
- **Medical use matching** for 14+ conditions
- **Flavor preference** tracking and matching
- **Personalized recommendations** based on purchase patterns
- **Social proof** via ratings and reviews
- **Educational responses** about terpenes and effects

---

## 🆘 Troubleshooting

### Issue: AI doesn't use Products tool
**Solution**: Check that the tool is connected to MotaBot AI node (ai_tool connection)

### Issue: No products returned
**Solution**: Verify Supabase credentials, check that products table has leafly_description IS NOT NULL

### Issue: Generic responses
**Solution**: Update system prompt to match the enhanced version

### Issue: Timeout errors
**Solution**: Add WHERE clauses to limit results (e.g., WHERE leafly_rating > 4.0 LIMIT 10)

---

## 📚 Related Documentation

- **Leafly Data Guide**: `leafly/ENHANCED_DATA_EXAMPLES.md`
- **SQL Query Examples**: `leafly/PROJECT_SUMMARY.md`
- **Integration Details**: `leafly/supabase-integration/README.md`
- **Scraper Documentation**: `leafly/SCRAPER_DOCUMENTATION.md`

---

## 🎉 Summary

Your MotaBot AI is now **10x smarter** with access to:
- ✅ 11,515 products with rich Leafly data
- ✅ Effects, medical uses, flavors, terpenes
- ✅ Ratings and reviews for social proof
- ✅ Detailed descriptions for customer education
- ✅ Smart filtering and recommendation capabilities

**Import the new workflow and start giving customers amazing personalized product recommendations!** 🚀

---

**Created**: October 14, 2025  
**Version**: 1.0 (Leafly Enhanced)  
**Status**: Production Ready  
**File**: `supabaseimport_LEAFLY_ENHANCED.json`

