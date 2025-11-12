# 🎯 Add These Supabase Query Tools to Your Working Workflow

## Your Current Setup (v5.200) ✅

You already have:
- ✅ Data Table Tools (Customers, Budtenders)
- ✅ Gmail Tool
- ✅ Code node that fetches CRM data

## What to Add: 4 Code Tool Nodes for Supabase Queries

Instead of creating separate workflows, **add these 4 Code Tool nodes** directly to your existing workflow!

---

## 🔧 How to Add Them in n8n:

### **Step 1: Add a Code Tool Node**

1. In n8n, click the **"+"** to add a new node
2. Search for **"Code Tool"** (not just "Code"!)
3. Add it to your canvas
4. Position it near your other tools (around position 576, 592)

### **Step 2: Configure Each Tool**

For each of the 4 tools below:
1. **Name** the node (e.g., "Get Customer Transactions")
2. **Description** - copy from below
3. **Code** - copy the JavaScript code
4. **Connect** the tool to your AI Agent node via `ai_tool` connection

---

## 🛠️ TOOL 1: Get Customer Transactions

**Node Configuration:**
- **Type:** Code Tool
- **Name:** `Get Customer Transactions`
- **Description:** `Get recent transaction history for a customer by their phone number. Returns transaction IDs, dates, locations, staff, and totals. Useful when customer asks 'what did I buy' or 'my purchase history'.`

**Code:**
```javascript
const phoneNumber = $input.item.json.phoneNumber || $input.item.json.phone_number;
const limit = $input.item.json.limit || 5;

const supabaseUrl = 'https://kiwmwoqrguyrcpjytgte.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0';

try {
  // Get customer
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

  // Get transactions
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

---

## 🛠️ TOOL 2: Get Transaction Items

**Node Configuration:**
- **Type:** Code Tool
- **Name:** `Get Transaction Items`
- **Description:** `Get detailed list of products purchased in a specific transaction. Requires transaction_id. Shows product names, quantities, and prices. Use after Get Customer Transactions to see what they bought.`

**Code:**
```javascript
const transactionId = $input.item.json.transactionId || $input.item.json.transaction_id;

const supabaseUrl = 'https://kiwmwoqrguyrcpjytgte.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0';

try {
  const response = await fetch(
    `${supabaseUrl}/rest/v1/transaction_items?transaction_id=eq.${transactionId}&select=*`,
    {
      headers: {
        'apikey': supabaseKey,
        'Authorization': `Bearer ${supabaseKey}`,
        'Accept': 'application/json'
      }
    }
  );

  const items = await response.json();

  return [{
    json: {
      transaction_id: transactionId,
      total_items: items.length,
      items: items.map(item => ({
        product: item.product_name || 'Unknown',
        brand: item.brand,
        quantity: item.quantity,
        price: `$${item.price}`
      }))
    }
  }];
} catch (error) {
  return [{ json: { error: error.message, items: [] } }];
}
```

---

## 🛠️ TOOL 3: Search Products Purchased

**Node Configuration:**
- **Type:** Code Tool
- **Name:** `Search Products Customer Bought`
- **Description:** `Search what products a customer has purchased historically. Can filter by product name. Shows how many times they bought it and total spent. Useful for 'have I bought Blue Dream before?'`

**Code:**
```javascript
const phoneNumber = $input.item.json.phoneNumber || $input.item.json.phone_number;
const searchTerm = ($input.item.json.searchTerm || $input.item.json.search_term || '').toLowerCase();

const supabaseUrl = 'https://kiwmwoqrguyrcpjytgte.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0';

try {
  // Get customer
  const custResp = await fetch(
    `${supabaseUrl}/rest/v1/customers?phone=eq.${encodeURIComponent(phoneNumber)}&select=member_id&limit=1`,
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
    return [{ json: { error: 'Customer not found', products: [] } }];
  }

  const memberId = customers[0].member_id;

  // Get transactions
  const txnResp = await fetch(
    `${supabaseUrl}/rest/v1/transactions?customer_id=eq.${memberId}&select=transaction_id`,
    {
      headers: {
        'apikey': supabaseKey,
        'Authorization': `Bearer ${supabaseKey}`,
        'Accept': 'application/json'
      }
    }
  );

  const transactions = await txnResp.json();
  const txnIds = transactions.map(t => t.transaction_id).join(',');

  if (!txnIds) {
    return [{ json: { products: [] } }];
  }

  // Get items
  const itemsResp = await fetch(
    `${supabaseUrl}/rest/v1/transaction_items?transaction_id=in.(${txnIds})&select=product_name,quantity,price`,
    {
      headers: {
        'apikey': supabaseKey,
        'Authorization': `Bearer ${supabaseKey}`,
        'Accept': 'application/json'
      }
    }
  );

  let items = await itemsResp.json();

  // Filter by search term if provided
  if (searchTerm) {
    items = items.filter(i => 
      (i.product_name || '').toLowerCase().includes(searchTerm)
    );
  }

  // Aggregate by product name
  const productMap = {};
  for (const item of items) {
    const name = item.product_name || 'Unknown';
    if (!productMap[name]) {
      productMap[name] = {
        product: name,
        times_purchased: 0,
        total_spent: 0
      };
    }
    productMap[name].times_purchased += 1;
    productMap[name].total_spent += parseFloat(item.price || 0);
  }

  const products = Object.values(productMap)
    .sort((a, b) => b.times_purchased - a.times_purchased)
    .slice(0, 10);

  return [{
    json: {
      total_unique_products: products.length,
      products: products.map(p => ({
        ...p,
        total_spent: `$${p.total_spent.toFixed(2)}`
      }))
    }
  }];
} catch (error) {
  return [{ json: { error: error.message, products: [] } }];
}
```

---

## 🛠️ TOOL 4: Calculate Customer Spending

**Node Configuration:**
- **Type:** Code Tool
- **Name:** `Calculate Customer Spending`
- **Description:** `Calculate total spending for a customer with optional date range. Shows total spent, average transaction, lifetime stats. Useful for 'how much have I spent this year?'`

**Code:**
```javascript
const phoneNumber = $input.item.json.phoneNumber || $input.item.json.phone_number;
const startDate = $input.item.json.startDate || $input.item.json.start_date || '2000-01-01';
const endDate = $input.item.json.endDate || $input.item.json.end_date || '2099-12-31';

const supabaseUrl = 'https://kiwmwoqrguyrcpjytgte.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0';

try {
  // Get customer
  const custResp = await fetch(
    `${supabaseUrl}/rest/v1/customers?phone=eq.${encodeURIComponent(phoneNumber)}&select=member_id,name,lifetime_value,total_visits&limit=1`,
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
    return [{ json: { error: 'Customer not found' } }];
  }

  const customer = customers[0];

  // Get transactions in date range
  const txnResp = await fetch(
    `${supabaseUrl}/rest/v1/transactions?customer_id=eq.${customer.member_id}&date=gte.${startDate}&date=lte.${endDate}&select=total_amount,date,shop_location`,
    {
      headers: {
        'apikey': supabaseKey,
        'Authorization': `Bearer ${supabaseKey}`,
        'Accept': 'application/json'
      }
    }
  );

  const transactions = await txnResp.json();

  const totalSpent = transactions.reduce((sum, t) => sum + parseFloat(t.total_amount || 0), 0);
  const avgTransaction = transactions.length > 0 ? totalSpent / transactions.length : 0;

  return [{
    json: {
      customer_name: customer.name,
      date_range: `${startDate} to ${endDate}`,
      transactions_in_period: transactions.length,
      total_spent: `$${totalSpent.toFixed(2)}`,
      average_transaction: `$${avgTransaction.toFixed(2)}`,
      lifetime_total: `$${customer.lifetime_value || 0}`,
      lifetime_visits: customer.total_visits || 0
    }
  }];
} catch (error) {
  return [{ json: { error: error.message } }];
}
```

---

## ✅ After Adding All 4 Tools:

1. **Connect each Code Tool** to your "MotaBot AI v5.200" node using `ai_tool` connections
2. **Update the System Prompt** to mention these 4 new tools
3. **Test** by sending a message like "What did I buy last time?"

---

## 📍 Tool Positions in n8n:

Spread them out below your current tools:
- Tool 1: `[576, 592]`
- Tool 2: `[704, 592]`
- Tool 3: `[576, 720]`
- Tool 4: `[704, 720]`

---

**This gives your AI 7 TOTAL TOOLS:**
1. ✅ Customers Data Points (Google Sheets rewards)
2. ✅ Budtenders Data Points
3. ✅ Budtenders DB 2025 Info
4. ✅ Gmail
5. 🆕 Get Customer Transactions
6. 🆕 Get Transaction Items
7. 🆕 Search Products Purchased
8. 🆕 Calculate Customer Spending

**Now the AI can query BOTH Google Sheets (rewards/points) AND Supabase CRM (transaction history)!** 🎉

