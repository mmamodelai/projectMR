# 🧪 Test Messages for MotaBot v5.200

**File Updated:** The workflow JSON has been fixed (syntax error removed)
**Ready to test:** Import the updated playground JSON into n8n

---

## ✅ **Best Test Messages to Verify Budtender Integration**

### **Test 1: Direct Budtender Question** ⭐ BEST TEST
**Send:**
```
Who helped me last time?
```

**Expected Response (with budtender data working):**
```
You usually work with Lizbeth Garcia - she's helped you 1 time! 
You've also worked with Devon Calonzo and Jimmy Silks.
```

**Expected Response (if budtender data NOT working):**
```
I can see your last visit was on Oct 9th! Want me to email you 
your full purchase history?
```

**Why this test:** This question SPECIFICALLY asks about staff, so the AI should use budtender data if it has access to it.

---

### **Test 2: Product Recommendation**
**Send:**
```
What should I try today?
```

**Expected Response (with budtender data):**
```
Your budtender Lizbeth Garcia knows your preferences well - 
she's helped you before! Stop by and ask for her.
```

**Expected Response (without budtender data):**
```
We've got great products! Blue Dream, Jack Herer, and more. 
Stop by Fire House Inc to see what's in today!
```

**Why this test:** AI should naturally mention the budtender when giving recommendations.

---

### **Test 3: Simple Greeting**
**Send:**
```
Hi
```

**Expected Response (with budtender data):**
```
Hey Stephen! Lizbeth Garcia will be happy to see you again! 
How can I help today?
```

**Expected Response (without budtender data):**
```
Hey Stephen! How can I help you today?
```

**Why this test:** Greeting is a natural place to mention the budtender relationship.

---

### **Test 4: Purchase History** (Your original test)
**Send:**
```
Hey what did I buy last time I was in? And how many transactions do you have for me
```

**Expected Response (with budtender data):**
```
You've made 3 visits with us, spending $140.76 total! 
Lizbeth Garcia helped you most recently. Want me to email 
you your detailed purchase history?
```

**Expected Response (without budtender data):**
```
I can see you've been here 3 times! For your exact purchase 
history, I'd need to pull that from our system. Would you 
like me to email you a detailed summary?
```

**Why this test:** Should use REAL data from CRM (3 transactions, $140.76 LTV), not make up numbers.

---

### **Test 5: Check CRM Data Accuracy**
**Send:**
```
How many times have I been there?
```

**Expected Response (correct CRM data):**
```
You've been here 3 times, Stephen! Your last visit was on 
October 9th. Thanks for coming back!
```

**What to check:**
- Should say "3 times" (not 2, not made up)
- Should mention last visit date
- Should use your actual name

---

### **Test 6: Budtender Availability**
**Send:**
```
Is Lizbeth working today?
```

**Expected Response (with budtender data):**
```
Great question! Lizbeth Garcia has been your favorite 
(33% of your visits)! I don't have the current schedule 
but call ahead to see when she's in.
```

**Expected Response (without budtender data):**
```
I don't have access to staff schedules, but you can call 
Fire House Inc to ask when she's working!
```

**Why this test:** Shows AI knows the relationship even when asked indirectly.

---

## 🔍 **How to Tell if Budtender Data is Working**

### ✅ **Signs it's WORKING:**
- AI mentions "Lizbeth Garcia" by name
- AI says "she's helped you X times"
- AI says percentages like "33% of your visits"
- AI mentions other budtenders (Devon Calonzo, Jimmy Silks)
- Uses REAL data (3 transactions, $140.76, Oct 9th last visit)

### ❌ **Signs it's NOT WORKING:**
- AI gives generic responses ("Stop by Fire House Inc!")
- AI makes up numbers (like "2 transactions" when you have 3)
- AI doesn't mention any budtender names
- AI says "I don't have access to that data"

---

## 📊 **What the AI Should Know About You (Stephen Clare)**

From the CRM database:
- **Name:** STEPHEN CLARE
- **Phone:** +16199773020
- **Total Visits:** 3
- **Lifetime Value:** $140.76
- **Last Visit:** October 9, 2025
- **VIP Status:** Regular

From the Transaction History:
- **Favorite Budtender:** Lizbeth Garcia (1 transaction, 33.3%)
- **Other Budtenders:** Devon Calonzo (1 transaction, 33.3%), Jimmy Silks (1 transaction, 33.3%)
- **Total Transactions:** 3

**If the AI gives different numbers, something is broken!**

---

## 🐛 **Troubleshooting**

### **Issue: AI makes up data (wrong transaction count)**
**Problem:** AI not accessing CRM database
**Solution:** Check "Prepare for AI + CRM Data" node logs in n8n
**Look for:** `console.log` messages showing database queries

### **Issue: AI doesn't mention budtenders**
**Problem:** Either:
1. Budtender query failing (check transactions table)
2. AI not reading the context properly (check system prompt)

**Solution:** 
1. Re-import the playground JSON (I just fixed a syntax error)
2. Test with "Who helped me last time?" (most direct test)

### **Issue: Node takes too long (>10 seconds)**
**Problem:** Database queries timing out
**Possible causes:**
- Supabase rate limiting
- Network issues
- Too many transactions to process

**Normal timing:** Should be 1-3 seconds for the Code node

---

## 🚀 **Action Items**

1. **Re-import the workflow:**
   - File: `motabot-ai/workflows/active/MotaBot wDB v5.100 COMPATIBLE playground.json`
   - I just fixed a syntax error (`\\n\\n'` → `\\n\\n`)

2. **Test with the BEST test message:**
   ```
   Who helped me last time?
   ```

3. **Check the response:**
   - Should mention "Lizbeth Garcia" 
   - Should say "she's helped you 1 time"
   - Should mention other budtenders

4. **If still not working:**
   - Check n8n execution logs
   - Look for errors in "Prepare for AI + CRM Data" node
   - Verify Supabase credentials are correct

---

**TL;DR: Send "Who helped me last time?" - If the AI mentions Lizbeth Garcia by name, the budtender integration is working!** ✅

