#!/usr/bin/env python3
"""
Diagnose Math Issues:
1. MOTA% calculation (why 274%?)
2. Lifetime value vs category spending
3. Recycling fee impact
"""
import os
from supabase import create_client

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTg0NTA1MSwiZXhwIjoyMDc1NDIxMDUxfQ.o-GId7meaTXwyB4neYjg05oPfRdasvOHs6FHZZyprLs")

sb = create_client(SUPABASE_URL, SUPABASE_KEY)

# Get Cherish Rider from screenshot
print("Finding Cherish Rider...")
customer = sb.table('customers_blaze').select('member_id, name, lifetime_value').ilike('name', '%Cherish%').ilike('name', '%Rider%').execute()

if not customer.data:
    print("Customer not found")
    exit()

member_id = customer.data[0]['member_id']
cached_ltv = customer.data[0]['lifetime_value']
name = customer.data[0]['name'].encode('ascii', 'ignore').decode('ascii')
print(f"Found: {name}")
print(f"Cached Lifetime Value: ${cached_ltv}\n")

# Get all transactions
trans = sb.table('transactions_blaze').select('transaction_id, seller_id, total_amount, date').eq('customer_id', member_id).eq('blaze_status', 'Completed').execute()
print(f"Total Transactions: {len(trans.data)}")

# Calculate actual total from transactions
actual_total = sum(t.get('total_amount', 0) or 0 for t in trans.data)
print(f"Actual Total from Transactions: ${actual_total:.2f}\n")

# Get Devon Calonzo's transactions (from screenshot - 97 visits)
print("=== DEVON CALONZO ANALYSIS ===")
devon_trans = [t for t in trans.data if t.get('seller_id') == '5b60a32c8c826712f7085aee']  # Devon's ID
print(f"Devon's Transactions: {len(devon_trans)}")

if devon_trans:
    devon_trans_ids = [t['transaction_id'] for t in devon_trans]
    devon_total = sum(t.get('total_amount', 0) or 0 for t in devon_trans)
    
    # Get items for Devon's transactions
    items = sb.table('transaction_items_blaze').select('product_name, brand, category, total_price, unit_price, quantity').in_('transaction_id', devon_trans_ids[:20]).execute()  # Sample
    
    print(f"Devon's Total Revenue: ${devon_total:.2f}")
    print(f"Sample of items (first 20 transactions):\n")
    
    total_item_revenue = 0
    mota_item_revenue = 0
    recycling_revenue = 0
    product_revenue = 0
    
    for item in items.data:
        product = item.get('product_name') or 'N/A'
        brand = (item.get('brand') or '').upper()
        category = item.get('category') or 'N/A'
        
        price = item.get('total_price')
        if price is None or price == 0:
            price = (item.get('unit_price') or 0) * (item.get('quantity') or 1)
        
        total_item_revenue += price
        
        # Check if MOTA
        if 'MOTA' in brand:
            mota_item_revenue += price
        
        # Check if recycling
        if category == 'FEES' or 'recycling' in product.lower():
            recycling_revenue += price
            print(f"  RECYCLING: {product[:50]} | ${price:.2f} | Brand: {brand}")
        else:
            product_revenue += price
            if 'MOTA' in brand:
                print(f"  PRODUCT:   {product[:50]} | ${price:.2f} | Brand: {brand}")
    
    print(f"\n  Total Item Revenue (sample): ${total_item_revenue:.2f}")
    print(f"  MOTA Item Revenue: ${mota_item_revenue:.2f}")
    print(f"  Recycling Revenue: ${recycling_revenue:.2f}")
    print(f"  Product Revenue: ${product_revenue:.2f}")
    print(f"  MOTA% (including recycling): {(mota_item_revenue / total_item_revenue * 100):.1f}%")
    print(f"  MOTA% (excluding recycling): {(mota_item_revenue / product_revenue * 100) if product_revenue > 0 else 0:.1f}%")

# Check spending by category
print("\n=== SPENDING BY CATEGORY (ALL TRANS) ===")
all_trans_ids = [t['transaction_id'] for t in trans.data]
all_items = []

for i in range(0, len(all_trans_ids), 100):
    batch = all_trans_ids[i:i+100]
    items_batch = sb.table('transaction_items_blaze').select('category, total_price, unit_price, quantity').in_('transaction_id', batch).execute()
    all_items.extend(items_batch.data)

category_totals = {}
for item in all_items:
    cat = item.get('category') or 'Unknown'
    price = item.get('total_price')
    if price is None or price == 0:
        price = (item.get('unit_price') or 0) * (item.get('quantity') or 1)
    
    if cat not in category_totals:
        category_totals[cat] = 0
    category_totals[cat] += price

print("Category Totals:")
for cat, total in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
    print(f"  {cat:<20} ${total:>8,.2f}")

total_from_items = sum(category_totals.values())
print(f"\nTotal from Items: ${total_from_items:.2f}")
print(f"Total from Transactions: ${actual_total:.2f}")
print(f"Difference: ${abs(total_from_items - actual_total):.2f}")

