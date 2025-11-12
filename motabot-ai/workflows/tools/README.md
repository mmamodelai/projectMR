# MotaBot v5.300 - Database Query Tool Workflows

## 📋 **Overview**

These are reusable sub-workflows that act as database query tools for any AI Agent in n8n.

Each tool:
- ✅ Has an "Execute Workflow Trigger" (can be called by other workflows)
- ✅ Accepts input parameters
- ✅ Queries Supabase CRM database
- ✅ Returns structured JSON data
- ✅ Can be used by ANY AI Agent workflow

---

## 🔧 **The 4 Tool Workflows**

### **1. Tool_Get_Customer_Transactions.json**

**Purpose:** Get transaction history for a customer by phone number

**Input Parameters:**
- `phoneNumber` (string, required) - Customer phone in E.164 format (e.g., +16199773020)
- `limit` (number, optional, default: 10) - Max transactions to return (max 50)

**Output:**
```json
{
  "customer_name": "STEPHEN CLARE",
  "member_id": "12345",
  "total_transactions": 3,
  "transactions": [
    {
      "transaction_id": "549912",
      "date": "2025-10-09",
      "location": "Fire House Inc",
      "staff": "Lizbeth Garcia",
      "total": 53.00,
      "payment": "Credit Card",
      "points_earned": 5
    }
  ]
}
```

---

### **2. Tool_Get_Transaction_Items.json**

**Purpose:** Get items purchased in a specific transaction

**Input Parameters:**
- `transactionId` (string, required) - The transaction ID to look up

**Output:**
```json
{
  "transaction_id": "549912",
  "total_items": 3,
  "items": [
    {
      "product_name": "Blue Dream 3.5g",
      "brand": "Premium",
      "category": "Flower",
      "strain_type": "Hybrid",
      "thc": 22.5,
      "cbd": 0.5,
      "quantity": 1,
      "price": 35.00,
      "total": 35.00
    }
  ]
}
```

---

### **3. Tool_Search_Products_Purchased.json**

**Purpose:** Search what products a customer has purchased

**Input Parameters:**
- `phoneNumber` (string, required) - Customer phone number
- `searchTerm` (string, optional) - Product name to search for (e.g., "Blue Dream")

**Output:**
```json
{
  "total_unique_products": 15,
  "products": [
    {
      "product_name": "Blue Dream 3.5g",
      "times_purchased": 5,
      "total_quantity": 7,
      "total_spent": 175.00
    }
  ]
}
```

---

### **4. Tool_Calculate_Spending.json**

**Purpose:** Calculate total spending for a customer with optional date filtering

**Input Parameters:**
- `phoneNumber` (string, required) - Customer phone number
- `startDate` (string, optional, default: '2000-01-01') - Start date YYYY-MM-DD
- `endDate` (string, optional, default: '2099-12-31') - End date YYYY-MM-DD

**Output:**
```json
{
  "customer_name": "STEPHEN CLARE",
  "date_range": {
    "start": "2025-01-01",
    "end": "2025-12-31"
  },
  "transactions_in_period": 3,
  "total_spent_in_period": 140.76,
  "average_transaction": 46.92,
  "lifetime_total": 140.76,
  "lifetime_visits": 3,
  "spending_by_location": [
    {
      "location": "Fire House Inc",
      "visits": 3,
      "spent": 140.76
    }
  ]
}
```

---

## 🚀 **How to Use in n8n**

### **Step 1: Import the 4 Tool Workflows**

1. Open n8n
2. Click "Import from File"
3. Import each of the 4 JSON files:
   - `Tool_Get_Customer_Transactions.json`
   - `Tool_Get_Transaction_Items.json`
   - `Tool_Search_Products_Purchased.json`
   - `Tool_Calculate_Spending.json`

### **Step 2: Get the Workflow IDs**

After importing, each workflow will have a unique ID in the URL:
```
https://your-n8n.com/workflow/abc123def456
                              ^^^^^^^^^^^^
                              This is the Workflow ID
```

Save these IDs - you'll need them!

### **Step 3: Use in an AI Agent Workflow**

Add a **"Workflow Tool"** node in your AI Agent workflow:

1. Add node → **"Tools" → "Workflow"**
2. Configure:
   - **Name:** `get_customer_transactions`
   - **Description:** `Get transaction history for a customer by phone number`
   - **Source:** `Database` (or `URL` if external n8n)
   - **Workflow ID:** `[paste the ID from Step 2]`
   - **Field to Return:** `response`
3. Connect to AI Agent node (via `ai_tool` connection)
4. Repeat for other 3 tools

### **Step 4: Test**

Send a test message to your AI Agent:
```
"What did I buy last time?"
```

The AI will:
1. Use `get_customer_transactions` tool
2. Get the transaction ID
3. Use `get_transaction_items` tool
4. Get the items
5. Respond with real data!

---

## 📊 **Tool Usage Examples**

### **Example 1: Recent Purchase Query**

**Customer asks:** "What did I buy last time?"

**AI uses:**
1. `get_customer_transactions` (phone=+16199773020, limit=1)
2. `get_transaction_items` (transactionId=549912)

**AI responds:** "On Oct 9th you got Blue Dream 3.5g, LA Kush vape, and a pre-roll for $53!"

---

### **Example 2: Spending Query**

**Customer asks:** "How much have I spent this year?"

**AI uses:**
1. `calculate_spending` (phone=+16199773020, startDate=2025-01-01, endDate=2025-12-31)

**AI responds:** "You've spent $140.76 across 3 visits this year! Your average is $46.92 per visit."

---

### **Example 3: Product Search**

**Customer asks:** "Have I bought Blue Dream before?"

**AI uses:**
1. `search_products_purchased` (phone=+16199773020, searchTerm="Blue Dream")

**AI responds:** "Yes! You bought Blue Dream 3.5g 5 times for a total of $175!"

---

## 🔧 **Maintenance**

### **To Update a Tool:**

1. Open the tool workflow in n8n
2. Edit the Code node
3. Save
4. The change is immediately available to all AI Agents using that tool!

### **To Add a New Tool:**

1. Create a new workflow with "Execute Workflow Trigger"
2. Add your query logic in a Code node
3. Export as JSON
4. Save to this folder
5. Import to n8n
6. Add as Workflow Tool to AI Agent

---

## 📁 **File Structure**

```
motabot-ai/workflows/tools/
├── README.md                                  ← This file
├── Tool_Get_Customer_Transactions.json        ← Tool 1
├── Tool_Get_Transaction_Items.json            ← Tool 2
├── Tool_Search_Products_Purchased.json        ← Tool 3
└── Tool_Calculate_Spending.json               ← Tool 4
```

---

## ✅ **Benefits of This Approach**

1. **Reusable** - Any AI Agent can use these tools
2. **Maintainable** - Update in one place, affects all agents
3. **Testable** - Can test tools independently
4. **Scalable** - Easy to add more tools
5. **Version Control** - Tools are tracked in Git

---

## 🎉 **Ready to Use!**

Import the 4 workflows into n8n, get their IDs, and configure your AI Agent to use them!

**Questions?** See `motabot-ai/workflows/active/V5.300_BUILD_GUIDE.md` for complete setup instructions.

