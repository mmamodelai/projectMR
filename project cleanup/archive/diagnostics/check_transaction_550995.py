#!/usr/bin/env python3
"""
Check transaction 550995 - why don't the items add up?
"""

from supabase import create_client

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

sb = create_client(SUPABASE_URL, SUPABASE_KEY)

# Get transaction
trans_response = sb.table('transactions').select('*').eq('transaction_id', '550995').execute()
trans = trans_response.data[0] if trans_response.data else None

if not trans:
    print("Transaction not found!")
    exit(1)

# Get items
items_response = sb.table('transaction_items').select('*').eq('transaction_id', '550995').execute()
items = items_response.data

print("=" * 80)
print("TRANSACTION 550995 ANALYSIS")
print("=" * 80)
print()
print(f"Date: {trans.get('date', 'N/A')}")
print(f"Customer ID: {trans.get('customer_id', 'N/A')}")
print(f"Staff: {trans.get('staff_name', 'N/A')}")
print()
print(f"Transaction Total: ${float(trans.get('total_amount', 0)):.2f}")
print(f"Number of Items: {len(items)}")
print()
print("=" * 80)
print("ITEMS IN TRANSACTION:")
print("=" * 80)

total_items = 0
for i, item in enumerate(items, 1):
    price = float(item.get('total_price', 0))
    qty = item.get('quantity', 1)
    product = item.get('product_name', 'N/A')
    
    print(f"{i}. {product[:50]}")
    print(f"   Price: ${price:.2f} x Qty: {qty}")
    print()
    
    total_items += price

print("=" * 80)
print("SUMMARY:")
print("=" * 80)
print(f"Sum of Items:        ${total_items:.2f}")
print(f"Transaction Total:   ${float(trans.get('total_amount', 0)):.2f}")
print(f"Difference:          ${float(trans.get('total_amount', 0)) - total_items:.2f}")
print()

if abs(float(trans.get('total_amount', 0)) - total_items) > 0.01:
    difference = float(trans.get('total_amount', 0)) - total_items
    print("ISSUE DETECTED!")
    print()
    print("Possible Causes:")
    print("1. TAXES: Transaction total includes taxes/fees, items don't")
    print("2. DISCOUNTS: Applied at checkout level, not item level")
    print("3. DATA IMPORT: CSV parsing issue during import")
    print("4. INCOMPLETE DATA: Some items not imported")
    print("5. TIPS/FEES: Additional charges added at transaction level")
    print()
    print(f"Missing Amount: ${difference:.2f}")
    print(f"Missing %: {(difference / float(trans.get('total_amount', 0)) * 100):.1f}%")
else:
    print("Items add up correctly!")

