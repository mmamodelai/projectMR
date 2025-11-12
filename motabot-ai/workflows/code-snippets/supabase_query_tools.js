// MotaBot v5.300: Database Query Tools
// These are CODE snippets for n8n Code nodes that act as AI tools

const supabaseUrl = 'https://kiwmwoqrguyrcpjytgte.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0';

// =====================================
// TOOL 1: Get Customer Transactions
// =====================================
// Node name: "Get Customer Transactions Tool"
// Description: "Query customer transaction history by phone number, with optional date filtering"

const phoneNumber = $fromAI('phoneNumber', 'Customer phone number in E.164 format (e.g., +16199773020)', 'string');
const limit = $fromAI('limit', 'Maximum number of transactions to return (default 10, max 50)', 'number') || 10;

try {
  // Get customer by phone
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
    return { json: { error: 'Customer not found', transactions: [] } };
  }
  
  const memberId = customers[0].member_id;
  
  // Get transactions
  const txnResp = await fetch(
    `${supabaseUrl}/rest/v1/transactions?customer_id=eq.${memberId}&select=*&order=date.desc&limit=${Math.min(limit, 50)}`,
    {
      headers: {
        'apikey': supabaseKey,
        'Authorization': `Bearer ${supabaseKey}`,
        'Accept': 'application/json'
      }
    }
  );
  
  const transactions = await txnResp.json();
  
  return {
    json: {
      customer_name: customers[0].name,
      member_id: memberId,
      total_transactions: transactions.length,
      transactions: transactions.map(t => ({
        transaction_id: t.transaction_id,
        date: t.date,
        location: t.shop_location,
        staff: t.staff_name,
        total: t.total_amount,
        payment: t.payment_type,
        points_earned: t.loyalty_points_earned
      }))
    }
  };
} catch (error) {
  return { json: { error: error.message, transactions: [] } };
}

// =====================================
// TOOL 2: Get Transaction Items
// =====================================
// Node name: "Get Transaction Items Tool"
// Description: "Get detailed items purchased in a specific transaction"

const transactionId = $fromAI('transactionId', 'The transaction ID to look up items for', 'string');

try {
  // Get transaction items
  const itemsResp = await fetch(
    `${supabaseUrl}/rest/v1/transaction_items?transaction_id=eq.${transactionId}&select=*`,
    {
      headers: {
        'apikey': supabaseKey,
        'Authorization': `Bearer ${supabaseKey}`,
        'Accept': 'application/json'
      }
    }
  );
  
  const items = await itemsResp.json();
  
  // Get product details for each item
  const productIds = [...new Set(items.map(i => i.product_id).filter(Boolean))];
  
  let products = {};
  if (productIds.length > 0) {
    const prodResp = await fetch(
      `${supabaseUrl}/rest/v1/products?id=in.(${productIds.join(',')})&select=id,name,brand,category,strain_type,thc_content,cbd_content`,
      {
        headers: {
          'apikey': supabaseKey,
          'Authorization': `Bearer ${supabaseKey}`,
          'Accept': 'application/json'
        }
      }
    );
    
    const prodList = await prodResp.json();
    products = Object.fromEntries(prodList.map(p => [p.id, p]));
  }
  
  return {
    json: {
      transaction_id: transactionId,
      total_items: items.length,
      items: items.map(item => {
        const product = products[item.product_id] || {};
        return {
          product_name: item.product_name || product.name || 'Unknown',
          brand: product.brand,
          category: product.category,
          strain_type: product.strain_type,
          thc: product.thc_content,
          cbd: product.cbd_content,
          quantity: item.quantity,
          price: item.price,
          total: item.total
        };
      })
    }
  };
} catch (error) {
  return { json: { error: error.message, items: [] } };
}

// =====================================
// TOOL 3: Search Products Purchased
// =====================================
// Node name: "Search Products Purchased Tool"  
// Description: "Search what products a customer has purchased, with optional filters"

const phoneNumber = $fromAI('phoneNumber', 'Customer phone number', 'string');
const searchTerm = $fromAI('searchTerm', 'Product name, brand, or category to search for (optional)', 'string') || '';
const category = $fromAI('category', 'Filter by product category (optional)', 'string') || '';

try {
  // Get customer
  const custResp = await fetch(
    `${supabaseUrl}/rest/v1/customers?phone=eq.${encodeURIComponent(phoneNumber)}&select=member_id&limit=1`,
    {
      headers: {
        'apikey': supabaseKey,
        'Authorization': `Bearer ${supabaseKey}`
      }
    }
  );
  
  const customers = await custResp.json();
  if (!customers || customers.length === 0) {
    return { json: { error: 'Customer not found', products: [] } };
  }
  
  const memberId = customers[0].member_id;
  
  // Get transactions to get transaction IDs
  const txnResp = await fetch(
    `${supabaseUrl}/rest/v1/transactions?customer_id=eq.${memberId}&select=transaction_id`,
    {
      headers: {
        'apikey': supabaseKey,
        'Authorization': `Bearer ${supabaseKey}`
      }
    }
  );
  
  const transactions = await txnResp.json();
  const txnIds = transactions.map(t => t.transaction_id);
  
  if (txnIds.length === 0) {
    return { json: { products: [] } };
  }
  
  // Get transaction items for those transactions
  const itemsResp = await fetch(
    `${supabaseUrl}/rest/v1/transaction_items?transaction_id=in.(${txnIds.join(',')})&select=product_name,quantity,price`,
    {
      headers: {
        'apikey': supabaseKey,
        'Authorization': `Bearer ${supabaseKey}`
      }
    }
  );
  
  let items = await itemsResp.json();
  
  // Filter by search term if provided
  if (searchTerm) {
    const search = searchTerm.toLowerCase();
    items = items.filter(i => 
      (i.product_name || '').toLowerCase().includes(search)
    );
  }
  
  // Aggregate by product name
  const productMap = {};
  for (const item of items) {
    const name = item.product_name || 'Unknown';
    if (!productMap[name]) {
      productMap[name] = {
        product_name: name,
        times_purchased: 0,
        total_quantity: 0,
        total_spent: 0
      };
    }
    productMap[name].times_purchased += 1;
    productMap[name].total_quantity += item.quantity || 1;
    productMap[name].total_spent += parseFloat(item.price || 0);
  }
  
  const products = Object.values(productMap).sort((a, b) => b.times_purchased - a.times_purchased);
  
  return {
    json: {
      total_unique_products: products.length,
      products: products.slice(0, 20) // Top 20
    }
  };
} catch (error) {
  return { json: { error: error.message, products: [] } };
}

// =====================================
// TOOL 4: Calculate Customer Spending
// =====================================
// Node name: "Calculate Spending Tool"
// Description: "Calculate total spending for a customer with optional date filtering"

const phoneNumber = $fromAI('phoneNumber', 'Customer phone number', 'string');
const startDate = $fromAI('startDate', 'Start date for filtering (YYYY-MM-DD format, optional)', 'string') || '2000-01-01';
const endDate = $fromAI('endDate', 'End date for filtering (YYYY-MM-DD format, optional)', 'string') || '2099-12-31';

try {
  // Get customer
  const custResp = await fetch(
    `${supabaseUrl}/rest/v1/customers?phone=eq.${encodeURIComponent(phoneNumber)}&select=member_id,name,lifetime_value,total_visits&limit=1`,
    {
      headers: {
        'apikey': supabaseKey,
        'Authorization': `Bearer ${supabaseKey}`
      }
    }
  );
  
  const customers = await custResp.json();
  if (!customers || customers.length === 0) {
    return { json: { error: 'Customer not found' } };
  }
  
  const customer = customers[0];
  
  // Get transactions in date range
  const txnResp = await fetch(
    `${supabaseUrl}/rest/v1/transactions?customer_id=eq.${customer.member_id}&date=gte.${startDate}&date=lte.${endDate}&select=total_amount,date,shop_location`,
    {
      headers: {
        'apikey': supabaseKey,
        'Authorization': `Bearer ${supabaseKey}`
      }
    }
  );
  
  const transactions = await txnResp.json();
  
  const totalSpent = transactions.reduce((sum, t) => sum + parseFloat(t.total_amount || 0), 0);
  const avgTransaction = transactions.length > 0 ? totalSpent / transactions.length : 0;
  
  // Group by location
  const byLocation = {};
  for (const txn of transactions) {
    const loc = txn.shop_location || 'Unknown';
    if (!byLocation[loc]) {
      byLocation[loc] = { location: loc, visits: 0, spent: 0 };
    }
    byLocation[loc].visits += 1;
    byLocation[loc].spent += parseFloat(txn.total_amount || 0);
  }
  
  return {
    json: {
      customer_name: customer.name,
      date_range: { start: startDate, end: endDate },
      transactions_in_period: transactions.length,
      total_spent_in_period: Math.round(totalSpent * 100) / 100,
      average_transaction: Math.round(avgTransaction * 100) / 100,
      lifetime_total: customer.lifetime_value,
      lifetime_visits: customer.total_visits,
      spending_by_location: Object.values(byLocation)
    }
  };
} catch (error) {
  return { json: { error: error.message } };
}

