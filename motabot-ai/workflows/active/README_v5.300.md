# MotaBot v5.300 - Database Query Agent

## 📁 **What's in This Folder:**

### **Main Workflow:**
- `MotaBot_v5.300_FIXED.json` - The complete, ready-to-import workflow

### **Documentation:**
- `IMPORT_FIXED_WORKFLOW.md` - Step-by-step import instructions
- `V5.300_WHATS_FIXED.md` - What was broken and how it was fixed
- `README_v5.300.md` - This file

---

## 🎯 **Quick Start:**

### **1. Import the Tool Workflows First**

Go to `../../tools/` and import these 4 files:
1. `Tool_Get_Customer_Transactions.json`
2. `Tool_Get_Transaction_Items.json`
3. `Tool_Search_Products_Purchased.json`
4. `Tool_Calculate_Spending.json`

### **2. Get the Workflow IDs**

For each imported tool workflow, open it and copy the ID from the URL:
```
https://your-n8n.com/workflow/[COPY-THIS-ID]
```

### **3. Import the Main Workflow**

Import `MotaBot_v5.300_FIXED.json`

### **4. Update Workflow IDs**

Open the main workflow and update these 4 nodes with YOUR workflow IDs:
- **Get Transactions Tool** → Paste your "Get Customer Transactions" workflow ID
- **Get Items Tool** → Paste your "Get Transaction Items" workflow ID
- **Search Products Tool** → Paste your "Search Products Purchased" workflow ID
- **Calculate Spending Tool** → Paste your "Calculate Spending" workflow ID

### **5. Activate!**

Click **"Active"** toggle at the top of the workflow.

---

## 🧪 **Test It:**

Send a text to your system:
```
"What did I buy last time?"
```

The AI will:
1. Use `get_customer_transactions` tool to find your recent transaction
2. Use `get_transaction_items` tool to see what products were in it
3. Respond with the actual products you bought!

---

## 🎉 **It's Working If:**

- ✅ No "fetch is not defined" errors
- ✅ No "The workflow did not return a response" errors
- ✅ AI responds with REAL data from your Supabase database
- ✅ You can ask follow-up questions and get accurate answers

---

## 📚 **More Info:**

- **Full Setup Guide:** `IMPORT_FIXED_WORKFLOW.md`
- **What Changed:** `V5.300_WHATS_FIXED.md`
- **Tool Workflows:** `../tools/README.md`

---

**Version:** 5.300  
**Status:** Production Ready  
**Architecture:** AI Agent + 4 Database Query Tools  
**Last Updated:** 2025-10-13  

