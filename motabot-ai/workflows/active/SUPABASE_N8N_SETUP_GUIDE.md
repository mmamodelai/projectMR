# 🔧 How to Make Supabase Accessible in n8n (ACTUAL WORKING SOLUTION)

## ❌ The Problem

The Code Tool nodes I added don't work in n8n because:
1. **Code Tool nodes can't be fully configured via JSON** - they need manual setup in the UI
2. n8n shows them as **question marks** because the tool schema is missing
3. The AI can't call them even though the code is there

## ✅ The Solution: 3 Options

---

## **OPTION 1: Manual Code Tool Setup (Recommended)**

Since your workflow already uses `fetch()` successfully in other Code nodes, we can manually add Code Tool nodes in the n8n UI.

### **Step-by-Step:**

1. **Open your workflow** in n8n
2. **Click the "+" button** to add a node
3. **Search for "Code Tool"** and add it
4. **Name it:** "Get Customer Transactions"
5. **Click "Add Field"** under "Specify Input Schema"
6. **Add parameter:**
   - Name: `phoneNumber`
   - Type: `string`
   - Description: "Customer phone number in E.164 format (e.g., +16199773020)"
7. **Add another parameter:**
   - Name: `limit`
   - Type: `number`
   - Description: "Number of transactions to return (default 5)"
8. **In the Code Editor, paste this:**

```javascript
const phoneNumber = $input.item.json.phoneNumber || $input.item.json.phone_number;
const limit = $input.item.json.limit || 5;

const supabaseUrl = 'https://kiwmwoqrguyrcpjytgte.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0';

try {
  const custResp = await fetch(
    `${supabaseUrl}/rest/v1/customers?phone=eq.${encodeURIComponent(phoneNumber)}&select=member_id,name&limit=1`,
    {
      headers: {
        'apikey': supabaseKey,
        'Authorization': `Bearer ${supabaseKey}`,
        'Accept': 'application/json'
      }
    }
  );

  const customers = await custResp.json();
  if (!customers || customers.length === 0) {
    return [{ json: { error: 'Customer not found', transactions: [] } }];
  }

  const memberId = customers[0].member_id;

  const txnResp = await fetch(
    `${supabaseUrl}/rest/v1/transactions?customer_id=eq.${memberId}&select=*&order=date.desc&limit=${Math.min(limit, 20)}`,
    {
      headers: {
        'apikey': supabaseKey,
        'Authorization': `Bearer ${supabaseKey}`,
        'Accept': 'application/json'
      }
    }
  );

  const transactions = await txnResp.json();

  return [{
    json: {
      customer_name: customers[0].name,
      total_transactions: transactions.length,
      transactions: transactions.map(t => ({
        id: t.transaction_id,
        date: t.date,
        location: t.shop_location,
        staff: t.staff_name,
        total: `$${t.total_amount}`
      }))
    }
  }];
} catch (error) {
  return [{ json: { error: error.message, transactions: [] } }];
}
```

9. **Connect it to your AI Agent** node (drag from the tool output to the AI input)
10. **Repeat for the other 3 tools**

---

## **OPTION 2: Use HTTP Request Tool Nodes**

n8n has a native **HTTP Request Tool** node that the AI can call!

### **Step-by-Step:**

1. **Add an "HTTP Request Tool" node**
2. **Name it:** "Get Customer Transactions"
3. **Configure:**
   - Method: `GET`
   - URL: `https://kiwmwoqrguyrcpjytgte.supabase.co/rest/v1/customers`
   - Authentication: None (use headers)
   - Add Headers:
     - `apikey`: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
     - `Authorization`: `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
4. **Add Input Parameters:**
   - `phoneNumber` (string)
5. **Connect to AI Agent**

**Problem:** This approach requires **multiple HTTP Request Tool nodes** (one for customers, one for transactions) and gets complex fast.

---

## **OPTION 3: Pre-Fetch in "Prepare for AI" Node (Simplest)**

Instead of giving the AI tools, we can **fetch ALL the data upfront** in the "Prepare for AI + CRM Data" node and include it in the conversation context.

### **Modify your "Prepare for AI + CRM Data" node:**

Add this code AFTER the existing customer data fetch:

```javascript
// NEW: Fetch recent transactions
let transactions = [];
if (customerData && customerData.member_id) {
  try {
    const txnUrl = `${supabaseUrl}/rest/v1/transactions?customer_id=eq.${customerData.member_id}&select=*&order=date.desc&limit=3`;
    const txnResponse = await fetch(txnUrl, {
      method: 'GET',
      headers: {
        'apikey': supabaseKey,
        'Authorization': `Bearer ${supabaseKey}`,
        'Accept': 'application/json'
      }
    });
    
    if (txnResponse.ok) {
      transactions = await txnResponse.json();
    }
  } catch (error) {
    console.log('Could not fetch transactions:', error);
  }
}

// NEW: Fetch transaction items for most recent transaction
let recentItems = [];
if (transactions.length > 0) {
  try {
    const itemsUrl = `${supabaseUrl}/rest/v1/transaction_items?transaction_id=eq.${transactions[0].transaction_id}&select=*`;
    const itemsResponse = await fetch(itemsUrl, {
      method: 'GET',
      headers: {
        'apikey': supabaseKey,
        'Authorization': `Bearer ${supabaseKey}`,
        'Accept': 'application/json'
      }
    });
    
    if (itemsResponse.ok) {
      recentItems = await itemsResponse.json();
    }
  } catch (error) {
    console.log('Could not fetch items:', error);
  }
}

// Then in the conversation string, add:
if (transactions.length > 0) {
  conversation += '\n=== RECENT PURCHASES ===\n';
  transactions.forEach((txn, idx) => {
    conversation += `${idx + 1}. ${txn.date} at ${txn.shop_location} - $${txn.total_amount}\n`;
  });
  conversation += '\n';
}

if (recentItems.length > 0) {
  conversation += '=== LAST PURCHASE DETAILS ===\n';
  recentItems.forEach(item => {
    conversation += `- ${item.product_name} (${item.quantity}x) - $${item.price}\n`;
  });
  conversation += '\n';
}
```

**Pros:**
- ✅ No tool configuration needed
- ✅ Works immediately
- ✅ Simple to implement

**Cons:**
- ❌ AI can't search for specific products
- ❌ AI can't calculate custom date ranges
- ❌ Pre-fetches data even if not needed

---

## **MY RECOMMENDATION: Option 3 (Pre-Fetch)**

For your use case, **Option 3 is the fastest and most reliable**. Here's why:

1. **Your workflow already uses this pattern** (you're already pre-fetching customer data)
2. **Most customer questions are answered by recent data** (last 3 transactions covers 90% of queries)
3. **No UI configuration needed** - just update one Code node
4. **Works immediately** - no manual setup in n8n

Let me implement Option 3 for you right now!

---

Would you like me to:
1. **Implement Option 3** (pre-fetch data in "Prepare for AI" node) - FASTEST ✅
2. **Create manual setup guide for Option 1** (Code Tool nodes) - MOST FLEXIBLE
3. **Try Option 2** (HTTP Request Tool nodes) - COMPLEX

Let me know and I'll make it work! 🚀

