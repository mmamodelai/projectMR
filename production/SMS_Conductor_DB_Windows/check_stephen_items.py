#!/usr/bin/env python3
"""
Check why we can't see Stephen's transaction items
"""
from supabase import create_client
import json

sb = create_client(
    'https://kiwmwoqrguyrcpjytgte.supabase.co',
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0'
)

# Stephen's transactions
transaction_ids = [548869, 548915, 549196]

print("=" * 80)
print("CHECKING STEPHEN CLARE'S TRANSACTION ITEMS")
print("=" * 80)

for trans_id in transaction_ids:
    print(f"\nTransaction {trans_id}:")
    
    # Try as integer
    items = sb.table('transaction_items').select('*').eq('transaction_id', trans_id).execute()
    print(f"  Found {len(items.data)} items (queried as int)")
    
    if not items.data:
        # Try as string
        items = sb.table('transaction_items').select('*').eq('transaction_id', str(trans_id)).execute()
        print(f"  Found {len(items.data)} items (queried as string)")
    
    if items.data:
        print(f"\n  Items:")
        for item in items.data[:10]:
            product = item.get('product_name', item.get('product_sku', 'Unknown'))
            qty = item.get('quantity', 0)
            price = item.get('unit_price', item.get('total_price', 0))
            print(f"    - {product}: Qty {qty} @ ${price}")
        
        # Show all columns for first item
        if items.data:
            print(f"\n  Sample item structure:")
            print(json.dumps(items.data[0], indent=4, default=str))
    else:
        print(f"  NO ITEMS FOUND!")

print("\n" + "=" * 80)
print("CHECKING TRANSACTION_ITEMS TABLE STRUCTURE")
print("=" * 80)

# Get a sample from transaction_items to see structure
sample = sb.table('transaction_items').select('*').limit(1).execute()
if sample.data:
    print("\nSample transaction_item record:")
    print(json.dumps(sample.data[0], indent=4, default=str))
else:
    print("\nNO DATA in transaction_items table!")

