# 🎯 COMPLETE DATA LINKAGE GUIDE: Phone Number → EVERYTHING

## What You Asked
> "from a phone number can we link all this info for the ai? like we need to get the WHOLE customer info/dataset you know?"

**Answer: YES! Here's exactly how:** ✅

---

## The Complete Chain

```
Phone Number: +16199773020
         ↓
1. customers.phone = '+16199773020'
         ↓
2. customers.member_id = '683cea4e022c82ba434de1df'  (⚠️ NOT customers.id!)
         ↓
3. transactions.customer_id = '683cea4e022c82ba434de1df'
         ↓
4. transactions.transaction_id = [548869, 548915, 549196, ...]
         ↓
5. transaction_items.transaction_id = 548869
         ↓
6. transaction_items.product_sku = 'FTGM100BRD'
         ↓
7. products.sku = 'FTGM100BRD'
         ↓
8. ✅ FULL PRODUCT DETAILS!
```

---

## The Tables & Their Structure

### 1. `customers` Table
**Key Fields:**
- `id`: Internal Supabase ID (8901) - **DON'T USE THIS!**
- **`member_id`**: The REAL customer ID ('683cea4e022c82ba434de1df') - **USE THIS!**
- `phone`: '+16199773020'
- `name`: 'STEPHEN CLARE'
- `email`: Email address
- `vip_status`: 'Casual', 'Regular', 'VIP'
- `lifetime_value`: $148.80
- `total_visits`: 3
- `churn_risk`: Risk score
- `days_since_last_visit`: Recency

**Query:**
```sql
SELECT * FROM customers WHERE phone = '+16199773020'
→ Gets member_id: '683cea4e022c82ba434de1df'
```

### 2. `transactions` Table
**Key Fields:**
- `id`: Internal ID
- **`transaction_id`**: The transaction number (548869, 548915, etc.)
- **`customer_id`**: Links to customers.member_id (NOT customers.id!)
- `date`: Transaction date
- `shop_location`: Store name
- `staff_name`: Budtender name
- `total_amount`: Total $$$
- `payment_type`: Payment method

**Query:**
```sql
SELECT * FROM transactions 
WHERE customer_id = '683cea4e022c82ba434de1df'
ORDER BY date DESC
→ Gets list of transaction_ids
```

### 3. `transaction_items` Table
**Key Fields:**
- `id`: Internal ID
- **`transaction_id`**: Links to transactions.transaction_id
- **`product_sku`**: Product SKU
- `product_name`: Product name
- `quantity`: How many
- `price`: Price per unit
- `total_price`: Total for this item

**Query:**
```sql
SELECT * FROM transaction_items 
WHERE transaction_id = 548869
→ Gets all items + their SKUs
```

### 4. `products` Table
**Key Fields:**
- **`sku`**: Product SKU (links to transaction_items.product_sku)
- `product_name`: Full product name
- `category`: Product category
- `brand`: Brand name
- `cost`: Cost price
- `in_stock`: Stock status
- `stock_age_days`: How old the stock is

**Query:**
```sql
SELECT * FROM products 
WHERE sku = 'FTGM100BRD'
→ Gets FULL product details
```

### 5. `staff` Table (Bonus!)
**Key Fields:**
- **`staff_id`**: Staff ID (links to transactions.staff_id if available)
- `staff_name`: Budtender name
- `role`: Job role
- `store_name`: Which store
- `performance_tier`: Performance rating

---

## 🚀 SHORTCUT: `customer_purchase_history` VIEW

**There's a pre-built view that joins EVERYTHING!**

```sql
SELECT * FROM customer_purchase_history 
WHERE phone = '+16199773020'
```

**Returns:**
- `member_id`: Customer ID
- `customer_name`: Full name
- `phone`: Phone number
- `vip_status`: VIP tier
- `transaction_id`: Transaction number
- `date`: Transaction date
- `total_amount`: Total spent
- `staff_name`: Budtender
- `shop_location`: Store
- **`items_purchased`**: Array of items
- **`products_bought`**: Array of products

**This is what the email used!** 🎉

---

## For the AI Agent: Query Strategy

### Option A: Use the VIEW (SIMPLEST)
```javascript
// In n8n "Prepare for AI" node:
const phone = currentMessage.phone_number;

// Query the view - gets EVERYTHING in one call!
const response = await fetch(
  `${supabaseUrl}/rest/v1/customer_purchase_history?phone=eq.${encodeURIComponent(phone)}`,
  {
    headers: {
      'apikey': supabaseKey,
      'Authorization': `Bearer ${supabaseKey}`
    }
  }
);

const data = await response.json();
// data[0] = first transaction with all details
// data[1] = second transaction with all details
// etc.
```

**✅ PROS:**
- ONE query gets everything
- Already formatted nicely
- Fast!

**❌ CONS:**
- Can't get individual product details beyond what's in the view

### Option B: Chain the Queries (DETAILED)
```javascript
// Step 1: Get customer
const customer = await fetch(`customers?phone=eq.${phone}`);
const member_id = customer.data[0].member_id;

// Step 2: Get transactions
const transactions = await fetch(`transactions?customer_id=eq.${member_id}`);

// Step 3: For each transaction, get items
for (const tx of transactions.data) {
  const items = await fetch(`transaction_items?transaction_id=eq.${tx.transaction_id}`);
  
  // Step 4: For each item, get full product details
  for (const item of items.data) {
    const product = await fetch(`products?sku=eq.${item.product_sku}`);
    // Now you have FULL product details!
  }
}
```

**✅ PROS:**
- Maximum detail
- Can get full product info (cost, stock, age, etc.)

**❌ CONS:**
- MANY queries (slow!)
- Complex

### Option C: HYBRID (RECOMMENDED!)
```javascript
// Use VIEW for quick summary
const summary = await fetch(`customer_purchase_history?phone=eq.${phone}&limit=5`);

// AI gets:
// - Customer name, phone, VIP status
// - Last 5 transactions with dates, totals, staff
// - Items purchased in each

// If AI needs MORE detail about a specific product:
// → Use Supabase Tool to query products table
```

**✅ BEST OF BOTH WORLDS!**

---

## Fix for Current n8n Workflow

### Problem in "Prepare for AI" Node
```javascript
// WRONG - uses customers.id (8901)
const customer = data[0];
const customer_id = customer.id;  // ❌ This is WRONG!

transactions.customer_id != 8901 → 0 results
```

### Fix
```javascript
// RIGHT - use customers.member_id
const customer = data[0];
const member_id = customer.member_id;  // ✅ This is CORRECT!

transactions.customer_id == '683cea4e022c82ba434de1df' → 3 results!
```

**OR EVEN BETTER:**
```javascript
// Use the customer_purchase_history VIEW!
const url = `${supabaseUrl}/rest/v1/customer_purchase_history?phone=eq.${encodeURIComponent(phoneNumber)}&order=date.desc&limit=10`;
```

---

## 🎯 Summary: What to Tell the AI

**The AI needs to know:**

1. **Phone number → `customer_purchase_history` view**
   - Gets: Name, Email, VIP status, recent transactions, items, products

2. **For deeper queries:**
   - `customers` table (use `member_id` NOT `id`!)
   - `transactions` table (links via `customer_id` = `customers.member_id`)
   - `transaction_items` table (links via `transaction_id`)
   - `products` table (links via `sku`)

3. **Critical Field Names:**
   - ⚠️ `customers.member_id` → `transactions.customer_id` (NOT `customers.id`!)
   - ⚠️ `transactions.transaction_id` → `transaction_items.transaction_id`
   - ⚠️ `transaction_items.product_sku` → `products.sku`

---

## Next Steps

1. **Update "Prepare for AI" node** to use `customer_purchase_history` view
2. **Update Supabase Tool nodes** to query by `member_id` not `id`
3. **Test with your phone** (+16199773020) to confirm full data retrieval
4. **Add transaction_items and products as AI tools** for deep dives

---

**YES, we can get the WHOLE customer dataset from just a phone number!** ✅🎉

