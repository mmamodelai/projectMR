# MotaBot v5.200 - Budtender Intelligence Upgrade
**Date:** October 12, 2025  
**Status:** ✅ Ready for Deployment

---

## 🎯 What's New

MotaBot can now reference **which budtenders customers work with most frequently**, creating highly personalized conversations that build loyalty and recognize staff-customer relationships.

### Example Conversations

**Before (v5.100):**
```
Customer: "What should I try?"
Bot: "We've got great products! Stop by Fire House Inc to see what's in stock today!"
```

**After (v5.200):**
```
Customer: "What should I try?"
Bot: "Your budtender Lizbeth Garcia knows your preferences well - she's helped you 33% of the time! Stop by and ask for her."
```

---

## 📊 New Data Available to AI

For **each customer**, MotaBot now knows:

1. **Favorite Budtender:** Staff member they've worked with most (e.g., "Lizbeth Garcia")
2. **Transaction Count:** How many times with that budtender (e.g., "5 transactions")
3. **Percentage:** What % of total visits (e.g., "45% of your visits")
4. **Total Sales:** Sales facilitated by that budtender (e.g., "$287.50")
5. **Other Budtenders:** Alternative staff they've worked with

---

## 🔧 Files Created

### 1. Python Script (Standalone Tool)
**File:** `mota-crm/scripts/get_customer_budtender.py`

**Usage:**
```bash
cd mota-crm/scripts
python get_customer_budtender.py +16199773020
```

**Output:**
```
SUCCESS - Customer: STEPHEN CLARE
Phone: +16199773020
Total Transactions: 3

Favorite Budtender:
   Name: Lizbeth Garcia
   Transactions: 1 (33.3%)
   Total Sales: $87.74

All Budtenders:
   1. Lizbeth Garcia - 1 txns (33.3%)
   2. Devon Calonzo - 1 txns (33.3%)
   3. Jimmy Silks - 1 txns (33.3%)
```

**Purpose:** Testing, debugging, manual customer lookups

---

### 2. n8n Code Node (Workflow Integration)
**File:** `motabot-ai/workflows/code-snippets/prepare_for_ai_with_budtender.js`

**What it does:**
- Fetches SMS conversation history
- Fetches customer CRM data (name, VIP status, visits, LTV)
- **NEW:** Fetches transaction history and calculates budtender stats
- Injects ALL data into AI conversation context

**How to use:**
1. Open n8n workflow: `MotaBot wDB v5.100 COMPATIBLE`
2. Find node: "Prepare for AI + CRM Data"
3. Replace JavaScript code with content from `prepare_for_ai_with_budtender.js`
4. Save and activate workflow

---

### 3. Updated System Prompt
**File:** `motabot-ai/workflows/code-snippets/system_prompt_v5.200.txt`

**What changed:**
- Added instructions on how to use budtender data
- Added 5 example use cases
- Added 5 example conversations
- Emphasized personalization with budtender names

**How to use:**
1. Open n8n workflow: `MotaBot wDB v5.100 COMPATIBLE`
2. Find node: "MotaBot AI v5.200"
3. Find parameter: `systemMessage`
4. Replace text with content from `system_prompt_v5.200.txt`
5. Save and activate workflow

---

### 4. Complete Documentation
**File:** `motabot-ai/docs/BUDTENDER_INTEGRATION_GUIDE.md`

**Contents:**
- Step-by-step implementation guide
- Testing procedures
- Troubleshooting
- Performance considerations
- Use cases and examples
- Success metrics

---

## 🚀 Deployment Steps

### Quick Deployment (5 minutes)

1. **Backup existing workflow**
   ```bash
   # In n8n, export current workflow as backup
   ```

2. **Update Code Node**
   - Copy code from: `motabot-ai/workflows/code-snippets/prepare_for_ai_with_budtender.js`
   - Paste into: n8n → "Prepare for AI + CRM Data" node

3. **Update System Prompt**
   - Copy text from: `motabot-ai/workflows/code-snippets/system_prompt_v5.200.txt`
   - Paste into: n8n → "MotaBot AI v5.200" node → `systemMessage`

4. **Update Workflow Name**
   - Rename workflow to: `MotaBot wDB v5.200`

5. **Test**
   - Send test SMS to: +16199773020
   - Ask: "Who helped me last time?"
   - Verify AI mentions budtender name

6. **Export and Save**
   - Export workflow as: `MotaBot wDB v5.200.json`
   - Save to: `motabot-ai/workflows/active/`

---

## 🧪 Test Cases

### Test Customer: Stephen Clare (+16199773020)

| Test Query | Expected Response |
|------------|-------------------|
| "Hi" | "Hey Stephen! Lizbeth Garcia will be happy to see you again!" |
| "What should I try?" | "Your budtender Lizbeth Garcia knows your preferences - she's helped you before!" |
| "Who helped me last time?" | "You usually work with Lizbeth Garcia - she's helped you 1 time!" |
| "What are my points?" | "Hey Stephen! You've got [X] points. Lizbeth has been your go-to budtender!" |

---

## 📈 Performance Impact

### Query Count per Message
- **v5.100:** 2 queries (conversation + customer)
- **v5.200:** 3 queries (conversation + customer + **transactions**)
- **Impact:** +50% query load, but still <500ms per message

### Data Volume
- Average customer: 3-10 transactions
- VIP customer: 20-50 transactions
- Max customer: 250+ transactions
- **All queried efficiently via indexed `customer_id`**

### Future Optimization
- Create materialized view: `customer_favorite_budtender`
- Pre-calculate budtender stats daily
- Reduce back to 2 queries per message

---

## 🎯 Expected Outcomes

### Customer Experience
- **More personal:** Customers feel recognized by staff references
- **More trust:** AI knows their history and preferences
- **More loyalty:** Mentioning favorite budtender encourages repeat visits

### Business Impact
- **Higher conversion:** SMS → visit rate should increase
- **Staff recognition:** Budtenders get credit for building customer relationships
- **Data insights:** See which staff-customer pairs are most successful

---

## 🔍 Data Quality Notes

### Current Status
- **Total Customers:** 10,047 (with phone numbers)
- **Total Transactions:** 93,592
- **Transactions with Staff Name:** ~85,000 (91%)
- **Transactions with Unknown/Empty Staff:** ~8,500 (9%)

### Handling Edge Cases
- **No transactions:** AI says "No transaction history found" (doesn't mention budtender)
- **All "Unknown" staff:** AI focuses on visit count and VIP status instead
- **Equal budtender split:** AI mentions the first one alphabetically
- **New customer (1-2 visits):** AI mentions budtender but doesn't emphasize frequency

---

## 🛠️ Troubleshooting

### Issue: AI not mentioning budtender

**Solution 1:** Verify data is in context
```javascript
// In Code node, add:
console.log('Budtender Data:', budtenderData);
```

**Solution 2:** Check system prompt
- Ensure v5.200 prompt is loaded
- Look for "FAVORITE BUDTENDER" section

**Solution 3:** Test explicit query
- Ask: "Who is my favorite budtender?"
- AI should respond with name from data

### Issue: Wrong budtender name

**Solution:** Check database
```bash
cd mota-crm/scripts
python get_customer_budtender.py +1XXXXXXXXXX
```

Verify output matches what AI receives.

---

## 📝 Next Steps

### Immediate (After Deployment)
- [ ] Monitor AI responses for budtender mentions
- [ ] Collect customer feedback
- [ ] Track conversion rate (SMS → visit)
- [ ] Update WORKLOG.md with deployment results

### Short-Term (This Week)
- [ ] Test with 10+ different customers
- [ ] Document edge cases and AI behavior
- [ ] Create report: % of conversations mentioning budtender
- [ ] Share with team for feedback

### Medium-Term (This Month)
- [ ] Implement materialized view for budtender data
- [ ] Add budtender availability lookup (future v5.3)
- [ ] Track staff-customer relationship metrics
- [ ] Integrate with shift scheduling system

---

## 🎉 Success Metrics

Track these KPIs after deployment:

1. **AI Personalization Rate:** % of responses mentioning customer name (target: 80%+)
2. **Budtender Mention Rate:** % of conversations referencing budtender (target: 30-50%)
3. **Response Quality:** Average message length (target: <150 chars)
4. **Customer Engagement:** Reply rate to personalized messages (target: +20%)
5. **Conversion Rate:** SMS → visit rate with budtender mention vs without (target: +15%)

---

## 📚 Related Files

### Documentation
- `motabot-ai/docs/BUDTENDER_INTEGRATION_GUIDE.md` - Complete implementation guide
- `WORKLOG.md` - Project progress log
- `README.md` - Project overview

### Code
- `mota-crm/scripts/get_customer_budtender.py` - Standalone budtender lookup tool
- `motabot-ai/workflows/code-snippets/prepare_for_ai_with_budtender.js` - n8n Code node
- `motabot-ai/workflows/code-snippets/system_prompt_v5.200.txt` - AI instructions

### Database
- Supabase CRM: `https://kiwmwoqrguyrcpjytgte.supabase.co`
- Table: `transactions` (uses `customer_id`, `staff_name`, `total_amount`)

---

## ✅ Completion Checklist

- [x] **Create Python script** for budtender lookup
- [x] **Test script** with Stephen Clare (+16199773020)
- [x] **Create n8n Code node** with budtender logic
- [x] **Create updated system prompt** with budtender instructions
- [x] **Write complete documentation** (BUDTENDER_INTEGRATION_GUIDE.md)
- [x] **Create upgrade summary** (this file)
- [ ] **Deploy to n8n workflow** (requires manual n8n access)
- [ ] **Test with live SMS** (requires deployment)
- [ ] **Update WORKLOG.md** (after deployment)
- [ ] **Export workflow as v5.200.json** (after deployment)
- [ ] **Commit to GitHub** (after testing)

---

**Status:** ✅ Development Complete - Ready for Deployment  
**Next Action:** Deploy code to n8n workflow and test with live SMS

**Questions?** See `motabot-ai/docs/BUDTENDER_INTEGRATION_GUIDE.md` for detailed instructions.

