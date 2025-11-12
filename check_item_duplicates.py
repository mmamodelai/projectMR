#!/usr/bin/env python3
"""
Check if transaction_items_blaze has duplicate items
"""
import os
from supabase import create_client

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTg0NTA1MSwiZXhwIjoyMDc1NDIxMDUxfQ.o-GId7meaTXwyB4neYjg05oPfRdasvOHs6FHZZyprLs")

sb = create_client(SUPABASE_URL, SUPABASE_KEY)

# Get a recent transaction
print("Getting a recent transaction...")
trans = sb.table('transactions_blaze').select('transaction_id, total_amount').eq('blaze_status', 'Completed').order('date', desc=True).limit(1).execute()

if not trans.data:
    print("No transactions found")
    exit()

trans_id = trans.data[0]['transaction_id']
trans_total = trans.data[0]['total_amount']

print(f"Transaction ID: {trans_id}")
print(f"Transaction Total: ${trans_total}")

# Get items for this transaction
items = sb.table('transaction_items_blaze').select('id, product_name, brand, quantity, unit_price, total_price').eq('transaction_id', trans_id).execute()

print(f"\nNumber of items: {len(items.data)}")
print("\nItems:")

item_total = 0
for i, item in enumerate(items.data, 1):
    product = (item.get('product_name') or 'N/A')[:40]
    qty = item.get('quantity', 0)
    unit = item.get('unit_price', 0)
    total = item.get('total_price')
    
    if total is None or total == 0:
        total = unit * qty
    
    item_total += total
    print(f"  {i}. [{item['id']}] {product} | Qty: {qty} | Unit: ${unit} | Total: ${total}")

print(f"\nSum of Item Totals: ${item_total:.2f}")
print(f"Transaction Total: ${trans_total:.2f}")
print(f"Difference: ${abs(item_total - trans_total):.2f}")

if abs(item_total - trans_total) > 0.01:
    print("\nWARNING: Item totals don't match transaction total!")
    print("This could be due to:")
    print("  1. Tax included in transaction but not items")
    print("  2. Discounts applied at transaction level")
    print("  3. Duplicate items in database")
    print("  4. Missing items")

# Check for exact duplicates
print("\n=== CHECKING FOR DUPLICATES ===")
seen = set()
duplicates = []

for item in items.data:
    key = (item.get('product_name'), item.get('brand'), item.get('quantity'), item.get('unit_price'))
    if key in seen:
        duplicates.append(item)
    seen.add(key)

if duplicates:
    print(f"Found {len(duplicates)} potential duplicates:")
    for dup in duplicates:
        print(f"  - {dup.get('product_name')} | ${dup.get('total_price')}")
else:
    print("No exact duplicates found in this transaction")

