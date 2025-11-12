# Supabase Query Tools for n8n - Query by Phone Number

These are HTTP Request nodes you can add to ANY n8n workflow to pull customer data by phone number.

## Credentials
- **Supabase URL**: `https://kiwmwoqrguyrcpjytgte.supabase.co`
- **API Key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0`

---

## 1. Get Conversation History by Phone Number
**What it gets**: All messages (inbound + outbound) for a phone number

**URL**:
```
={{ 'https://kiwmwoqrguyrcpjytgte.supabase.co/rest/v1/messages?select=*&phone_number=eq.' + encodeURIComponent($json.phone_number) + '&order=timestamp.desc&limit=50' }}
```

**Headers**:
- `apikey`: [API key from above]
- `Authorization`: `Bearer [API key from above]`
- `Accept`: `application/json`

**Returns**: Last 50 messages for that phone number

---

## 2. Get Customer Info by Phone Number
**What it gets**: Customer profile, points, visits, VIP status

**URL**:
```
={{ 'https://kiwmwoqrguyrcpjytgte.supabase.co/rest/v1/customers?select=*&phone=eq.' + encodeURIComponent($json.phone_number) + '&limit=1' }}
```

**Headers**: Same as above

**Returns**: 
- `member_id`, `first_name`, `last_name`, `email`, `phone`
- `total_visits`, `total_lifetime_value`, `vip_status`
- `last_visit_date`, `days_since_last_visit`, `churn_risk`

---

## 3. Get Transaction History by Phone Number
**What it gets**: All purchases by this customer (uses JOIN)

**URL**:
```
={{ 'https://kiwmwoqrguyrcpjytgte.supabase.co/rest/v1/transactions?select=*,customers!inner(phone,first_name,last_name,email)&customers.phone=eq.' + encodeURIComponent($json.phone_number) + '&order=transaction_date.desc&limit=20' }}
```

**Headers**: Same as above

**Returns**: Last 20 transactions with:
- Transaction ID, date, total amount, staff name
- Customer info embedded
- Sorted by most recent first

---

## 4. Get Purchase Items by Phone Number
**What it gets**: Detailed product purchases (uses multi-JOIN)

**URL**:
```
={{ 'https://kiwmwoqrguyrcpjytgte.supabase.co/rest/v1/transaction_items?select=*,transactions!inner(transaction_date,total_amount,customers!inner(phone,first_name,last_name)),products(product_name,category,brand,thc_content,cbd_content)&transactions.customers.phone=eq.' + encodeURIComponent($json.phone_number) + '&order=transactions.transaction_date.desc&limit=50' }}
```

**Headers**: Same as above

**Returns**: Last 50 items purchased with:
- Item details (quantity, price, discount)
- Product details (name, category, THC/CBD)
- Transaction date and total
- Customer info

---

## 5. Get Customer Product Affinity by Phone Number
**What it gets**: Top products this customer buys

**URL**:
```
={{ 'https://kiwmwoqrguyrcpjytgte.supabase.co/rest/v1/customer_product_affinity?select=*,customers!inner(phone),products(product_name,category)&customers.phone=eq.' + encodeURIComponent($json.phone_number) + '&order=purchase_count.desc&limit=10' }}
```

**Headers**: Same as above

**Returns**: Top 10 products with:
- Product name, category
- Purchase count, total spent
- Affinity score

---

## How to Use in n8n

### Option A: Add as HTTP Request nodes
1. Create HTTP Request node
2. Set Method: GET
3. Paste URL (with expression)
4. Authentication: "Predefined Credential Type" → "Supabase API"
5. Add your Supabase credentials
6. Send Headers: ON
7. Add headers: `apikey`, `Authorization`, `Accept`

### Option B: Use in Code Node with fetch()
```javascript
const phoneNumber = $json.phone_number;
const supabaseUrl = 'https://kiwmwoqrguyrcpjytgte.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...';

// Get customer transactions
const url = `${supabaseUrl}/rest/v1/transactions?select=*,customers!inner(phone,first_name)&customers.phone=eq.${encodeURIComponent(phoneNumber)}&limit=20`;

const response = await fetch(url, {
  headers: {
    'apikey': supabaseKey,
    'Authorization': `Bearer ${supabaseKey}`,
    'Accept': 'application/json'
  }
});

const transactions = await response.json();
return { json: { transactions } };
```

---

## Quick Copy-Paste for AI Tools

### Tool 1: Get Customer Profile
**Description**: "Get customer info by phone number including points, visits, VIP status"
**URL**: `customers?select=*&phone=eq.[PHONE]`

### Tool 2: Get Transaction History
**Description**: "Get customer transaction history by phone number"
**URL**: `transactions?select=*,customers!inner(phone,first_name,last_name,email)&customers.phone=eq.[PHONE]&limit=20`

### Tool 3: Get Purchase Items
**Description**: "Get detailed purchase history with product names by phone number"
**URL**: `transaction_items?select=*,transactions!inner(transaction_date,customers!inner(phone)),products(product_name,category)&transactions.customers.phone=eq.[PHONE]&limit=50`

---

## Testing URLs (Direct Browser Test)

Test these in your browser (they'll work because anon key allows reads):

1. **Customer Info**:
```
https://kiwmwoqrguyrcpjytgte.supabase.co/rest/v1/customers?select=*&phone=eq.%2B16199773020&apikey=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0
```

2. **Transaction History**:
```
https://kiwmwoqrguyrcpjytgte.supabase.co/rest/v1/transactions?select=*,customers!inner(phone,first_name)&customers.phone=eq.%2B16199773020&limit=5&apikey=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0
```

---

**Use these queries to build your AI tools! All queries work by phone number without modifying the database!** 🚀

