# Quick Setup: Database Query Tools for n8n

## 🚀 **Setup in 5 Minutes**

## ⚠️ **IMPORTANT: These are v2 (FIXED) Workflows**

The original tool workflows had a bug (`fetch is not defined`). These v2 workflows use **HTTP Request nodes** instead of `fetch()` and will work correctly in n8n!

### **Step 1: Import the 4 Tool Workflows** (2 minutes)

1. Open your n8n instance
2. Click **"Workflows"** in the left sidebar
3. Click **"Import from File"**
4. Import each file:
   - ✅ `Tool_Get_Customer_Transactions.json`
   - ✅ `Tool_Get_Transaction_Items.json`
   - ✅ `Tool_Search_Products_Purchased.json`
   - ✅ `Tool_Calculate_Spending.json`

---

### **Step 2: Get the Workflow IDs** (1 minute)

For each imported workflow:
1. Click on it to open
2. Look at the URL in your browser:
   ```
   https://your-n8n.com/workflow/abc123def456
   ```
3. Copy the ID part (`abc123def456`)

**Save these 4 IDs somewhere!** You'll need them in Step 3.

**Example:**
```
Tool: Get Customer Transactions → ID: abc123
Tool: Get Transaction Items → ID: def456
Tool: Search Products → ID: ghi789
Tool: Calculate Spending → ID: jkl012
```

---

### **Step 3: Update the Main Workflow** (2 minutes)

1. Open `MotaBot v5.300 - Database Query Agent` workflow
2. Find the **"Get Transactions Tool"** node
3. Click on it
4. In **"Workflow ID"** field, paste the ID from Step 2 for that tool
5. Repeat for all 4 tool nodes:
   - Get Transactions Tool → paste ID `abc123`
   - Get Items Tool → paste ID `def456`
   - Search Products Tool → paste ID `ghi789`
   - Calculate Spending Tool → paste ID `jkl012`

---

### **Step 4: Test It!** (30 seconds)

1. Activate the `MotaBot v5.300` workflow
2. Send a test SMS: **"What did I buy last time?"**
3. Watch the AI:
   - ✅ Use Tool 1 (Get Transactions)
   - ✅ Use Tool 2 (Get Items)
   - ✅ Respond with real data!

---

## 🎯 **Quick Reference**

### **Tool Names for AI Agent:**

| Tool Node Name | Tool Function Name | What It Does |
|----------------|-------------------|--------------|
| Get Transactions Tool | `get_customer_transactions` | Get transaction history |
| Get Items Tool | `get_transaction_items` | Get items in a transaction |
| Search Products Tool | `search_products_purchased` | Search products purchased |
| Calculate Spending Tool | `calculate_spending` | Calculate spending totals |

---

## 📋 **Checklist**

- [ ] Imported all 4 tool workflows to n8n
- [ ] Got all 4 workflow IDs from URLs
- [ ] Updated MotaBot v5.300 workflow with correct IDs
- [ ] Activated MotaBot v5.300 workflow
- [ ] Tested with "What did I buy last time?"
- [ ] AI successfully used tools and responded!

---

## 🐛 **Troubleshooting**

### **"Workflow not found" error:**
→ Double-check the Workflow ID in the tool node matches the imported workflow ID

### **"No tools available" error:**
→ Make sure all 4 tool nodes are connected to the AI Agent via `ai_tool` connections

### **AI not using tools:**
→ Check the AI system message includes instructions for using tools

### **Tools returning errors:**
→ Test the tool workflow directly (click "Test workflow") to see the error

---

## ✅ **You're Done!**

Your AI Agent can now query the Supabase database on-demand! 🎉

**Next:** See `README.md` for detailed tool documentation and examples.

