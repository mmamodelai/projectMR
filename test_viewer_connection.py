#!/usr/bin/env python3
"""
Test Viewer Connection - Simulate What IC Viewer Does
"""

from supabase import create_client, Client

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

print("=" * 80)
print("SIMULATING IC VIEWER - Testing Connection")
print("=" * 80)
print()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Step 1: Get a recent customer with transactions
print("Step 1: Finding customer with recent activity...")
recent_trans = supabase.table('transactions_blaze') \
    .select('customer_id, transaction_id, date, total_amount') \
    .not_.is_('customer_id', 'null') \
    .order('date', desc=True) \
    .limit(1) \
    .execute()

if not recent_trans.data:
    print("No recent transactions found!")
    exit(1)

trans = recent_trans.data[0]
customer_id = trans['customer_id']
transaction_id = trans['transaction_id']

print(f"Found transaction: {transaction_id[:20]}...")
print(f"  Date: {trans['date'][:10]}")
print(f"  Amount: ${trans['total_amount']:.2f}")
print(f"  Customer ID: {customer_id[:20]}...")
print()

# Step 2: Get customer info (what viewer does)
print("Step 2: Loading customer from customers_blaze...")
cust_result = supabase.table('customers_blaze') \
    .select('member_id, name, first_name, last_name, phone, email, text_opt_in') \
    .eq('member_id', customer_id) \
    .execute()

if cust_result.data:
    cust = cust_result.data[0]
    name = cust.get('name') or f"{cust.get('first_name', '')} {cust.get('last_name', '')}".strip()
    print(f"  Customer: {name}")
    print(f"  Phone: {cust.get('phone') or 'None'}")
    print(f"  Email: {cust.get('email') or 'None'}")
    print(f"  SMS Opt-In: {cust.get('text_opt_in')}")
else:
    print("  Customer not found!")
print()

# Step 3: Get transactions for this customer (what viewer does)
print("Step 3: Loading transactions from transactions_blaze...")
trans_result = supabase.table('transactions_blaze') \
    .select('transaction_id, date, total_amount, payment_type, seller_id, blaze_status') \
    .eq('customer_id', customer_id) \
    .order('date', desc=True) \
    .limit(5) \
    .execute()

print(f"  Found {len(trans_result.data)} transactions:\n")

for t in trans_result.data:
    print(f"    {t['date'][:10]} | ${t['total_amount']:.2f} | {t['payment_type'] or 'N/A'} | {t['blaze_status']}")

print()

# Step 4: Get items for first transaction (what viewer does when you click)
print("Step 4: Loading items from transaction_items_blaze...")
print(f"  For transaction: {transaction_id[:30]}...")
print()

items_result = supabase.table('transaction_items_blaze') \
    .select('id, product_name, brand, quantity, total_price') \
    .eq('transaction_id', transaction_id) \
    .order('total_price', desc=True) \
    .execute()

print(f"  Found {len(items_result.data)} items:\n")

if not items_result.data:
    print("    NO ITEMS FOUND!")
    print("    This means items are missing or transaction_id doesn't match")
else:
    for item in items_result.data:
        name = item.get('product_name') or 'N/A'
        brand = item.get('brand') or 'Unknown'
        qty = item.get('quantity', 0)
        price = item.get('total_price', 0)
        
        print(f"    {name[:50]:<50} | {brand:<15} | {qty:.1f} | ${price:.2f}")

print()
print("=" * 80)
print("VERDICT")
print("=" * 80)

if items_result.data:
    all_have_names = all(item.get('product_name') for item in items_result.data)
    
    if all_have_names:
        print("VIEWER SHOULD WORK PERFECTLY!")
        print("  - Customer found")
        print("  - Transactions found")
        print("  - Items found")
        print("  - All items have product names")
    else:
        print("VIEWER WILL SHOW ITEMS, BUT SOME AS 'N/A'")
        missing_count = sum(1 for item in items_result.data if not item.get('product_name'))
        print(f"  - {missing_count} items missing product_name")
else:
    print("PROBLEM: No items found for this transaction!")
    print("  - Check if transaction_items_blaze is empty")
    print("  - Check if transaction_id format matches")

print("=" * 80)

