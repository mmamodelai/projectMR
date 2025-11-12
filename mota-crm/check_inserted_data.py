#!/usr/bin/env python3
"""
Quick check of what's being inserted into transaction_items_blaze
"""

from supabase import create_client
import json

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTg0NTA1MSwiZXhwIjoyMDc1NDIxMDUxfQ.o-GId7meaTXwyB4neYjg05oPfRdasvOHs6FHZZyprLs"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=" * 70)
print("TRANSACTION ITEMS - SAMPLE DATA CHECK")
print("=" * 70)
print()

# Get total count
try:
    count_result = supabase.table('transaction_items_blaze').select('id', count='exact').limit(1).execute()
    total = count_result.count
    print(f"Total items in database: {total:,}")
    print()
except Exception as e:
    print(f"Error getting count: {e}")
    print()

# Get latest 5 items
print("Latest 5 items inserted:")
print("-" * 70)
try:
    result = supabase.table('transaction_items_blaze').select('*').order('id', desc=True).limit(5).execute()
    
    for i, item in enumerate(result.data, 1):
        print(f"\n{i}. ID: {item.get('id')}")
        print(f"   Transaction: {item.get('transaction_id')}")
        print(f"   Product: {item.get('product_name')} (SKU: {item.get('product_sku')})")
        print(f"   Brand: {item.get('brand')}")
        print(f"   Category: {item.get('category')}")
        print(f"   Quantity: {item.get('quantity')}")
        print(f"   Unit Price: ${item.get('unit_price')}")
        print(f"   Total: ${item.get('total_price')}")
        print(f"   Final Price: ${item.get('final_price')}")
        
except Exception as e:
    print(f"Error: {e}")

print()
print("=" * 70)

# Check for duplicates in last 100 items
print("\nChecking for duplicates in last 100 items...")
print("-" * 70)
try:
    result = supabase.table('transaction_items_blaze').select(
        'transaction_id, product_id, quantity, unit_price'
    ).order('id', desc=True).limit(100).execute()
    
    seen = set()
    duplicates = []
    
    for item in result.data:
        key = (
            item.get('transaction_id'),
            item.get('product_id'),
            item.get('quantity'),
            item.get('unit_price')
        )
        if key in seen:
            duplicates.append(key)
        seen.add(key)
    
    if duplicates:
        print(f"WARNING: Found {len(duplicates)} duplicate keys in last 100 items:")
        for dup in duplicates[:3]:
            print(f"   - transaction: {dup[0]}, product: {dup[1]}, qty: {dup[2]}, price: {dup[3]}")
    else:
        print("SUCCESS: No duplicates found in last 100 items - dedupe is working!")
    
except Exception as e:
    print(f"Error checking duplicates: {e}")

print()
print("=" * 70)

# Check date range of items
print("\nDate range of inserted items:")
print("-" * 70)
try:
    # Get earliest and latest items
    earliest = supabase.table('transaction_items_blaze').select('id, transaction_id').order('id', desc=False).limit(1).execute()
    latest = supabase.table('transaction_items_blaze').select('id, transaction_id').order('id', desc=True).limit(1).execute()
    
    if earliest.data and latest.data:
        print(f"Earliest item ID: {earliest.data[0].get('id')}")
        print(f"Latest item ID: {latest.data[0].get('id')}")
        print(f"Total range: {latest.data[0].get('id') - earliest.data[0].get('id') + 1:,} items")
    
except Exception as e:
    print(f"Error: {e}")

print()
print("=" * 70)

