# MotaBot Budtender Integration Guide
**Version 5.200 - October 12, 2025**

## Overview
This guide explains how to integrate budtender/staff data into the MotaBot AI workflow, allowing personalized conversations that reference which budtenders customers have worked with most frequently.

---

## 🎯 What This Adds

### Before (v5.100)
MotaBot knew:
- Customer name, VIP status
- Total visits, lifetime value
- Last visit date
- Conversation history

### After (v5.200)
MotaBot NOW knows:
- **Favorite budtender** (most frequent staff member)
- **Number of transactions** with that budtender
- **Percentage of visits** with that budtender
- **Total sales** facilitated by that budtender
- **Other budtenders** the customer has worked with

---

## 📊 Data Source

### Supabase CRM Database
**Table:** `transactions`
**Key Fields:**
- `customer_id` - Links to customer record
- `staff_name` - Name of budtender who helped
- `total_amount` - Transaction total
- `date` - Transaction date

### Query Logic
1. Get `member_id` from `customers` table using `phone` number
2. Fetch ALL transactions for that `customer_id`
3. Group by `staff_name` and count transactions
4. Calculate percentage, total sales per budtender
5. Sort by transaction count (descending)
6. Return favorite budtender + top 3

---

## 🔧 Implementation Steps

### Step 1: Update "Prepare for AI + CRM Data" Code Node

**Location:** n8n workflow → "Prepare for AI + CRM Data" node

**Replace the existing JavaScript code with:**

```javascript
// See: motabot-ai/workflows/code-snippets/prepare_for_ai_with_budtender.js
// (Copy the full code from that file)
```

**What it does:**
1. Fetches SMS conversation history (existing)
2. Fetches customer CRM data (existing)
3. **NEW:** Fetches all transactions for the customer
4. **NEW:** Calculates budtender statistics
5. **NEW:** Identifies favorite budtender
6. Injects ALL data into conversation context

**Key Changes:**
- Added `memberId` variable from customer lookup
- Added `budtenderData` fetch and calculation logic
- Added budtender section to conversation context string
- Added `favorite_budtender` and `budtender_data` to output JSON

---

### Step 2: Update System Prompt

**Location:** n8n workflow → "MotaBot AI v5.200" node → `systemMessage` parameter

**Replace the existing system prompt with:**

```
// See: motabot-ai/workflows/code-snippets/system_prompt_v5.200.txt
// (Copy the full text from that file)
```

**What changed:**
- Updated version to v5.200
- Added "FAVORITE BUDTENDER" section to data description
- Added 5 example use cases for budtender data
- Added 5 example conversations using budtender names
- Updated personalization examples to include budtender references
- Emphasized the value of budtender history in building customer relationships

---

### Step 3: Update Workflow Sticky Note

**Location:** n8n workflow → "Workflow Info" sticky note

**Update the content to:**

```markdown
## 🚀 MotaBot v5.200 - BUDTENDER INTELLIGENCE

**NEW BUDTENDER INTEGRATION:**
✅ Favorite budtender detection
✅ Transaction count per budtender
✅ Percentage analysis
✅ Top 3 budtenders per customer

**PREVIOUS FEATURES:**
✅ Direct Supabase CRM queries
✅ Enhanced AI instructions for CRM data
✅ Product search via natural language
✅ Purchase history via conversation context

**CONNECTED TO:**
- Supabase CRM (93K+ transactions)
- Customer Data (10,047 customers with phone #s)
- Product Catalog (14K+ products)
- Transaction History (by staff member)
```

---

## 🧪 Testing the Integration

### Test Case 1: Basic Budtender Query

**Send SMS to Conductor:** `Who helped me last time?`

**Expected AI Response:**
```
You usually work with [Budtender Name] - they've helped you [X] times! Want me to email you your full visit history?
```

### Test Case 2: Product Recommendation with Budtender

**Send SMS:** `What should I try today?`

**Expected AI Response:**
```
Your budtender [Name] knows your preferences well - they've helped you [X] times! Stop by and they'll hook you up.
```

### Test Case 3: VIP with Favorite Budtender

**Send SMS:** `What are my points?`

**Expected AI Response:**
```
Hey [Customer]! You've got [X] points and you're [VIP Status]! [Budtender Name] is your go-to with [Y]% of your visits.
```

### Test Customer
**Phone:** +16199773020 (Stephen Clare)
**Expected Budtender:** Lizbeth Garcia (33.3%, 1 txn) OR Devon Calonzo (33.3%, 1 txn) OR Jimmy Silks (33.3%, 1 txn)

---

## 📈 Performance Considerations

### Query Cost
**Existing (v5.100):**
- 1 query: SMS conversation history
- 1 query: Customer CRM data
- **Total: 2 queries per message**

**New (v5.200):**
- 1 query: SMS conversation history
- 1 query: Customer CRM data
- **1 query: Transaction history (NEW)**
- **Total: 3 queries per message**

### Optimization Notes
- Transaction query uses `customer_id` index (fast)
- Only selects 2 fields (`staff_name`, `total_amount`)
- Calculation happens in-memory (no additional DB queries)
- Results cached in conversation context

### Future Optimization
- Create materialized view: `customer_favorite_budtender`
- Update view daily/weekly
- Reduce to 2 queries per message again

---

## 🎯 Use Cases for Budtender Data

### 1. Personalized Greetings
```
Customer: "Hi"
Bot: "Hey [Name]! [Budtender Name] will be happy to see you again - you two are at [X] visits together!"
```

### 2. Product Recommendations
```
Customer: "What's good today?"
Bot: "[Budtender Name] has helped you [X] times - they know your style! Stop by and ask for them."
```

### 3. Building Loyalty
```
Customer: "Thanks for the help!"
Bot: "Anytime! [Budtender Name] has been your go-to for [X]% of your visits - glad we could help!"
```

### 4. Alternative Suggestions
```
Customer: "Is [Budtender A] working today?"
Bot: "Not sure their schedule but [Budtender B] and [Budtender C] have also helped you before!"
```

### 5. VIP Recognition
```
Customer: "What's my VIP status?"
Bot: "You're [Status] with [X] visits! [Budtender Name] has facilitated $[Y] in sales - you're a rockstar!"
```

---

## 🔍 Data Quality

### Current Status (as of Oct 12, 2025)
- **Total Customers:** 10,047 (with phone numbers)
- **Total Transactions:** 93,592 (verified complete)
- **Transactions with Staff Name:** ~85,000 (91%)
- **Transactions with Unknown/Empty Staff:** ~8,500 (9%)

### Handling Missing Data
The script gracefully handles:
- Customers with no transactions → "No transaction history found"
- Transactions with no staff name → Skipped, not counted
- Customers with only "Unknown" staff → "No budtender information found"

---

## 🚀 Deployment Checklist

- [ ] **Backup existing workflow** (`MotaBot wDB v5.100 COMPATIBLE.json`)
- [ ] **Update "Prepare for AI + CRM Data" Code node** with new JavaScript
- [ ] **Update "MotaBot AI v5.200" node** with new system prompt
- [ ] **Update Workflow Info sticky note** to v5.200
- [ ] **Test with Stephen Clare** (+16199773020)
- [ ] **Verify budtender name appears** in AI response
- [ ] **Test with multiple customers** (different budtender histories)
- [ ] **Export workflow** as `MotaBot wDB v5.200.json`
- [ ] **Update WORKLOG.md** with deployment notes
- [ ] **Update motabot-ai/README.md** with v5.200 features
- [ ] **Commit to GitHub**

---

## 📝 Workflow Versioning

### Version History
- **v5.000:** Initial n8n workflow (basic SMS bot)
- **v5.100:** Added CRM database access (customer profile data)
- **v5.200:** **Added budtender intelligence** (staff interaction history)

### File Naming Convention
```
MotaBot wDB v5.200.json
```
- `wDB` = "with Database"
- `v5.200` = Major.Minor.Patch (thousandths decimals)

---

## 🛠️ Troubleshooting

### Issue: Budtender data not showing in AI response

**Check 1:** Verify `budtenderData` is populated
- Add `console.log(budtenderData)` in Code node
- Check n8n execution logs

**Check 2:** Verify conversation context includes budtender section
- Add `console.log(conversation)` before return
- Look for "=== FAVORITE BUDTENDER ===" section

**Check 3:** Verify AI is reading the context
- Test with explicit query: "Who is my favorite budtender?"
- AI should respond with the name from context

**Check 4:** Verify transactions exist for customer
- Use CRM viewer to check transaction count
- Ensure `staff_name` is populated (not null or "Unknown")

### Issue: AI not mentioning budtender in natural conversation

**Possible causes:**
- System prompt not updated
- AI model not following instructions
- Response too long (>150 chars) so AI skips budtender mention

**Solutions:**
- Verify system prompt includes v5.200 content
- Add more explicit examples to system prompt
- Test with different AI models (Gemini vs GPT-4)

### Issue: Incorrect budtender name

**Check:**
- Verify `staff_name` in transactions table
- Check for typos or inconsistent naming
- Consider implementing staff name normalization

---

## 📊 Success Metrics

### Expected Outcomes
- **Personalization:** 80%+ of responses include customer's name
- **Budtender Mention:** 30-50% of conversations reference budtender
- **Customer Satisfaction:** Positive feedback about personalization
- **Repeat Visits:** Customers asking for specific budtenders by name

### KPIs to Track
1. % of AI responses mentioning budtender
2. Customer response rate after budtender mention
3. Conversion rate (SMS → visit) with vs without budtender mention
4. Average response length (should stay <150 chars)

---

## 🔗 Related Documentation

- `MOTABOT_V5.100_README.md` - Previous version documentation
- `N8N_INTEGRATION_GUIDE.md` - General n8n integration guide
- `SUPABASE_OPTIMIZATION_PLAN.md` - Database performance strategies
- `CONDUCTOR_ARCHITECTURE.md` - SMS system architecture

---

## 🎯 Future Enhancements

### Planned (v5.3+)
- [ ] Budtender availability lookup (Google Calendar integration)
- [ ] Budtender specialties (e.g., "flower expert", "concentrates pro")
- [ ] Customer-budtender match scoring
- [ ] Proactive budtender suggestions based on product inquiry

### Under Consideration
- [ ] Budtender performance metrics (sales, customer satisfaction)
- [ ] Cross-location budtender tracking
- [ ] Budtender shift schedules in CRM
- [ ] Customer request routing to favorite budtender

---

**Last Updated:** October 12, 2025  
**Version:** 5.200  
**Status:** Ready for Deployment

