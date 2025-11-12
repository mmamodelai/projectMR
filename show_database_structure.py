#!/usr/bin/env python3
"""
Show Database Structure - Visual Flow
See exactly what tables exist and how they link
"""

from supabase import create_client, Client

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTg0NTA1MSwiZXhwIjoyMDc1NDIxMDUxfQ.o-GId7meaTXwyB4neYjg05oPfRdasvOHs6FHZZyprLs"

print("=" * 80)
print("DATABASE STRUCTURE - COMPLETE FLOW")
print("=" * 80)
print()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("STEP 1: WHAT TABLES EXIST?")
print("-" * 80)
print()

tables = {
    'customers_blaze': 'Customer information from Blaze',
    'transactions_blaze': 'Transaction records (receipts)',
    'transaction_items_blaze': 'Individual items in each transaction',
    'products_blaze': 'Product catalog',
    'employees_blaze': 'Budtenders/staff'
}

for table, desc in tables.items():
    try:
        result = supabase.table(table).select('*', count='exact').limit(0).execute()
        print(f"  {table:<30} {result.count:>10,} records - {desc}")
    except:
        print(f"  {table:<30} ERROR")

print()
print("=" * 80)
print("STEP 2: THE FLOW (How They Connect)")
print("=" * 80)
print()
print("  customers_blaze")
print("      |")
print("      | (member_id)")
print("      |")
print("      v")
print("  transactions_blaze  <--- One customer has many transactions")
print("      |")
print("      | (transaction_id)")
print("      |")
print("      v")
print("  transaction_items_blaze  <--- One transaction has many items")
print("      |")
print("      | (product_id)")
print("      |")
print("      v")
print("  products_blaze  <--- Item links to product for details")
print()

print("=" * 80)
print("STEP 3: REAL EXAMPLE - Follow One Customer")
print("=" * 80)
print()

# Get a customer
customer = supabase.table('customers_blaze') \
    .select('member_id, name, phone') \
    .not_.is_('name', 'null') \
    .limit(1) \
    .execute()

if customer.data:
    c = customer.data[0]
    member_id = c['member_id']
    print(f"CUSTOMER: {c['name']}")
    print(f"  member_id: {member_id}")
    print(f"  phone:     {c['phone']}")
    print()
    
    # Get their transactions
    transactions = supabase.table('transactions_blaze') \
        .select('transaction_id, date, total_amount') \
        .eq('customer_id', member_id) \
        .order('date', desc=True) \
        .limit(3) \
        .execute()
    
    print(f"  HAS {len(transactions.data)} RECENT TRANSACTIONS:")
    print()
    
    for i, txn in enumerate(transactions.data, 1):
        print(f"  TRANSACTION #{i}:")
        print(f"    transaction_id: {txn['transaction_id']}")
        print(f"    date:          {txn['date'][:10]}")
        print(f"    total:         ${txn['total_amount']:.2f}")
        
        # Get items for this transaction
        items = supabase.table('transaction_items_blaze') \
            .select('product_id, product_name, brand, quantity, total_price') \
            .eq('transaction_id', txn['transaction_id']) \
            .limit(5) \
            .execute()
        
        print(f"    HAS {len(items.data)} ITEMS:")
        
        for item in items.data[:3]:  # Show first 3 items
            prod_name = item.get('product_name') or 'NO NAME'
            brand = item.get('brand') or 'NO BRAND'
            print(f"      - {prod_name[:40]:<40} | {brand:<15} | ${item['total_price']:.2f}")
        
        if len(items.data) > 3:
            print(f"      ... and {len(items.data) - 3} more items")
        
        print()

print()
print("=" * 80)
print("STEP 4: WHAT YOUR VIEWER QUERIES")
print("=" * 80)
print()
print("When you click a customer in IC Viewer, it:")
print()
print("  1. Gets customer from: customers_blaze")
print("     WHERE member_id = 'ABC123'")
print()
print("  2. Gets their transactions from: transactions_blaze")
print("     WHERE customer_id = 'ABC123'")
print()
print("  3. When you click a transaction, gets items from: transaction_items_blaze")
print("     WHERE transaction_id = 'TXN456'")
print()
print("  4. (Optional) Can lookup product details in: products_blaze")
print("     WHERE product_id = 'PROD789'")
print()

print("=" * 80)
print("STEP 5: THE DUPLICATE PROBLEM EXPLAINED")
print("=" * 80)
print()

# Find a transaction with duplicates
dup_check = supabase.table('transaction_items_blaze') \
    .select('transaction_id, product_name') \
    .not_.is_('product_name', 'null') \
    .limit(100) \
    .execute()

# Count duplicates
from collections import Counter
trans_counts = Counter([item['transaction_id'] for item in dup_check.data])
dup_trans = [tid for tid, count in trans_counts.items() if count > 10]

if dup_trans:
    example_trans = dup_trans[0]
    
    items = supabase.table('transaction_items_blaze') \
        .select('id, product_name, brand, quantity, total_price') \
        .eq('transaction_id', example_trans) \
        .execute()
    
    print(f"Example: Transaction {example_trans[:20]}...")
    print(f"  Has {len(items.data)} items in database")
    print()
    
    # Group by product to show duplicates
    product_counts = Counter([item.get('product_name') for item in items.data])
    
    print("  Items (with duplicate count):")
    for product, count in product_counts.most_common(5):
        if product:
            print(f"    {product[:40]:<40} appears {count}x  {'<-- DUPLICATE!' if count > 1 else ''}")
    
    print()
    print("  THIS IS THE PROBLEM!")
    print("  Same items inserted multiple times during sync.")
    print("  Should be ~5 items, but showing ~25 because 5 items x 5 duplicates.")

print()
print("=" * 80)
print("SIMPLE SUMMARY")
print("=" * 80)
print()
print("TABLE NAMES (These are the 'new' Blaze tables):")
print("  - customers_blaze          (customers)")
print("  - transactions_blaze       (receipts)")
print("  - transaction_items_blaze  (line items)")
print("  - products_blaze           (product catalog)")
print()
print("FLOW:")
print("  customer -> transactions -> items -> products")
print()
print("PROBLEMS:")
print("  1. transaction_items_blaze has 2.2M rows (should be 1M)")
print("  2. Items duplicated 5-6x from multiple sync runs")
print("  3. 582k items missing product_name (shows as blank)")
print()
print("=" * 80)

