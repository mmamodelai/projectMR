#!/usr/bin/env python3
"""
Check CURRENT State - After Your Rebuild
See if duplicates still exist or if it's clean now
"""

from supabase import create_client, Client

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTg0NTA1MSwiZXhwIjoyMDc1NDIxMDUxfQ.o-GId7meaTXwyB4neYjg05oPfRdasvOHs6FHZZyprLs"

print("=" * 80)
print("CURRENT DATABASE STATE CHECK (After Your Rebuild)")
print("=" * 80)
print()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Check for duplicates
print("1. CHECKING FOR DUPLICATES")
print("-" * 80)

# Get a recent transaction
recent_trans = supabase.table('transactions_blaze') \
    .select('transaction_id, date, total_amount, customer_id') \
    .order('date', desc=True) \
    .limit(5) \
    .execute()

print(f"Checking 5 most recent transactions:\n")

for txn in recent_trans.data:
    trans_id = txn['transaction_id']
    
    # Get items for this transaction
    items = supabase.table('transaction_items_blaze') \
        .select('id, product_name, brand, quantity, total_price') \
        .eq('transaction_id', trans_id) \
        .execute()
    
    # Count duplicates
    from collections import Counter
    product_counts = Counter([
        (item.get('product_name'), item.get('quantity'), item.get('total_price'))
        for item in items.data
    ])
    
    has_dupes = any(count > 1 for count in product_counts.values())
    status = "DUPLICATES!" if has_dupes else "Clean"
    
    print(f"  Transaction: ${txn['total_amount']:.2f} on {txn['date'][:10]}")
    print(f"    Items: {len(items.data)} total")
    print(f"    Unique items: {len(product_counts)}")
    print(f"    Status: {status}")
    
    if has_dupes:
        print("    Duplicated items:")
        for (product, qty, price), count in product_counts.items():
            if count > 1:
                print(f"      - {product[:40]} appears {count}x")
    print()

print()
print("2. CHECK PRODUCT NAMES")
print("-" * 80)

items_result = supabase.table('transaction_items_blaze') \
    .select('*', count='exact') \
    .limit(0) \
    .execute()

items_with_names = supabase.table('transaction_items_blaze') \
    .select('*', count='exact') \
    .not_.is_('product_name', 'null') \
    .limit(0) \
    .execute()

total_items = items_result.count
items_with_name = items_with_names.count
missing_names = total_items - items_with_name

print(f"  Total items:       {total_items:,}")
print(f"  With product_name: {items_with_name:,}")
print(f"  Missing names:     {missing_names:,}")

if missing_names == 0:
    print("  Status: CLEAN - All items have names!")
else:
    pct_missing = (missing_names / total_items) * 100
    print(f"  Status: {pct_missing:.1f}% missing product names")

print()
print("3. SAMPLE RECENT ITEMS")
print("-" * 80)

sample = supabase.table('transaction_items_blaze') \
    .select('transaction_id, product_id, product_name, brand, quantity, total_price') \
    .order('id', desc=True) \
    .limit(10) \
    .execute()

for item in sample.data:
    name = item.get('product_name') or 'NULL/MISSING'
    brand = item.get('brand') or 'NULL/MISSING'
    print(f"  {name[:50]:<50} | {brand:<15} | ${item.get('total_price', 0):.2f}")

print()
print("=" * 80)
print("VERDICT")
print("=" * 80)

if missing_names == 0 and not any(has_dupes for txn in recent_trans.data):
    print("DATABASE IS CLEAN!")
    print("  - No duplicates in recent transactions")
    print("  - All items have product names")
    print("  - Ready to wire up viewer!")
else:
    print("STILL HAS ISSUES:")
    if missing_names > 0:
        print(f"  - {missing_names:,} items missing product_name")
    print("  - May have duplicate items")
    print("  - Needs cleanup before viewer will work perfectly")

print("=" * 80)

