# 🎯 Import the FIXED MotaBot v5.300 Workflow

## ✅ What Was Fixed

The **"Prepare for AI"** node was using `fetch()` which doesn't work in n8n Code nodes. 

**OLD (BROKEN):**
```javascript
const response = await fetch(url, { ... });  // ❌ fetch is not defined
```

**NEW (FIXED):**
```javascript
// Simple context - AI will use tools for detailed data
const conversation = `Customer Phone: ${phoneNumber}\n\nCustomer Question: ${incomingMessage}`;
```

Now the AI Agent will use its **4 database query tools** to fetch data, not the Prepare node!

---

## 📥 **How to Import:**

### **Step 1: Import the Main Workflow**

1. In n8n, go to **Workflows** → **Import from File**
2. Select: `MotaBot_v5.300_FIXED.json`
3. The workflow will import with all tool configurations!

### **Step 2: Verify Tool Workflow IDs**

The imported workflow already has these Workflow IDs configured:

- **Get Transactions Tool**: `ofKuX9TlLmRMSpfB`
- **Get Items Tool**: `gYEHBHKI7NjMfyPa`
- **Search Products Tool**: `dWNHqwcxiEHSFKHU`
- **Calculate Spending Tool**: `dq2l9e41YEs1zJkA`

**Make sure these match YOUR tool workflow IDs!** 

To check:
1. Open each tool workflow in n8n
2. Look at the URL: `https://your-n8n.com/workflow/[THIS-IS-THE-ID]`
3. Update the `workflowId` in each tool node if they don't match

### **Step 3: Check Tool Input Schemas**

Each tool node already has `specifyInputSchema: true` configured:

✅ **Get Transactions Tool** expects:
- `phoneNumber` (String)
- `limit` (Number, optional)

✅ **Get Items Tool** expects:
- `transactionId` (String)

✅ **Search Products Tool** expects:
- `phoneNumber` (String)
- `searchTerm` (String, optional)

✅ **Calculate Spending Tool** expects:
- `phoneNumber` (String)
- `startDate` (String, optional)
- `endDate` (String, optional)

---

## 🧪 **Test It!**

### **Test 1: Manual Test**

1. Click on the **"Prepare for AI"** node
2. Click **"Test step"**
3. Paste this input:
```json
{
  "phone_number": "+16199773020",
  "incoming_message": "What did I buy last time?",
  "message_id": "test-123"
}
```
4. Click **"Test step"** again
5. Output should be:
```json
{
  "chatInput": "Customer Phone: +16199773020\n\nCustomer Question: What did I buy last time?",
  "phone_number": "+16199773020",
  "message_id": "test-123"
}
```

### **Test 2: Full Workflow Test**

1. Create a test message in Supabase:
```sql
INSERT INTO messages (phone_number, content, direction, status)
VALUES ('+16199773020', 'What did I buy last time?', 'inbound', 'unread');
```

2. Click **"Execute workflow"** at the top

3. The AI should:
   - Call `get_customer_transactions` tool
   - Get transaction data
   - Respond with real data!

---

## 🎉 **Success Checklist:**

- ✅ Workflow imports without errors
- ✅ All 4 tool nodes show "Connected" with green checkmarks
- ✅ "Prepare for AI" node no longer has `fetch()` error
- ✅ AI Agent can call tools and get database results
- ✅ AI responds with accurate customer data

---

## 🐛 **Troubleshooting:**

### **"The workflow did not return a response"**
- Check that the tool sub-workflows are active
- Verify Workflow IDs match
- Test each tool workflow individually

### **"fetch is not defined"**
- This should be fixed! The "Prepare for AI" node no longer uses `fetch()`
- If you still see this, re-import the `MotaBot_v5.300_FIXED.json`

### **"No parameters are set up to be filled by AI"**
- Toggle **"Specify Input Schema"** ON for each tool
- Add the input parameters as shown in Step 3 above
- Save the workflow

---

**Ready to go live!** 🚀

