#!/usr/bin/env python3
"""
Check Database Integrity - Verify Products and Transactions Linking
Check if products database was nuked and if transactions are properly linked
"""

from supabase import create_client, Client

# Supabase connection
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTg0NTA1MSwiZXhwIjoyMDc1NDIxMDUxfQ.o-GId7meaTXwyB4neYjg05oPfRdasvOHs6FHZZyprLs"

print("=" * 80)
print("DATABASE INTEGRITY CHECK")
print("=" * 80)
print()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 1. Check what tables exist
print("1. CHECKING TABLES")
print("-" * 80)

tables_to_check = [
    'customers_blaze',
    'transactions_blaze',
    'transaction_items_blaze',
    'products_blaze',
    'employees_blaze'
]

for table in tables_to_check:
    try:
        result = supabase.table(table).select('*', count='exact').limit(0).execute()
        print(f"  {table:<30} EXISTS - {result.count:,} records")
    except Exception as e:
        print(f"  {table:<30} ERROR: {e}")

print()

# 2. Check transaction_items linkage
print("2. TRANSACTION ITEMS ANALYSIS")
print("-" * 80)

try:
    # Total items
    items_result = supabase.table('transaction_items_blaze').select('*', count='exact').limit(0).execute()
    total_items = items_result.count
    print(f"  Total transaction items: {total_items:,}")
    
    # Items with products
    items_with_products = supabase.table('transaction_items_blaze') \
        .select('*', count='exact') \
        .not_.is_('product_name', 'null') \
        .limit(0) \
        .execute()
    print(f"  Items with product_name: {items_with_products.count:,}")
    
    # Items with brands
    items_with_brands = supabase.table('transaction_items_blaze') \
        .select('*', count='exact') \
        .not_.is_('brand', 'null') \
        .limit(0) \
        .execute()
    print(f"  Items with brand:        {items_with_brands.count:,}")
    
    # Missing product names
    missing_products = total_items - items_with_products.count
    if missing_products > 0:
        print(f"  WARNING: {missing_products:,} items missing product_name!")
    
    print()
    
    # Sample items to see what data looks like
    print("  Sample transaction items:")
    sample = supabase.table('transaction_items_blaze') \
        .select('transaction_id, product_id, product_name, brand, quantity, total_price') \
        .limit(5) \
        .execute()
    
    for item in sample.data:
        print(f"    {item.get('product_name', 'NO NAME'):<40} | {item.get('brand', 'NO BRAND'):<20} | ${item.get('total_price', 0):.2f}")
    
except Exception as e:
    print(f"  ERROR: {e}")

print()

# 3. Check products_blaze table
print("3. PRODUCTS DATABASE CHECK")
print("-" * 80)

try:
    # Total products
    products_result = supabase.table('products_blaze').select('*', count='exact').limit(0).execute()
    total_products = products_result.count
    print(f"  Total products in products_blaze: {total_products:,}")
    
    if total_products == 0:
        print("  WARNING: Products table is EMPTY! This might be the 'nuke' issue.")
    
    # Sample products
    if total_products > 0:
        print("\n  Sample products:")
        sample_products = supabase.table('products_blaze') \
            .select('product_id, name, sku, retail_price, is_active') \
            .limit(5) \
            .execute()
        
        for prod in sample_products.data:
            print(f"    {prod.get('name', 'NO NAME'):<40} | SKU: {prod.get('sku', 'N/A'):<15} | ${prod.get('retail_price', 0):.2f}")
    
except Exception as e:
    print(f"  ERROR checking products_blaze: {e}")

print()

# 4. Check if items can be linked to products
print("4. LINKAGE CHECK: Items -> Products")
print("-" * 80)

try:
    # Get sample items with product_ids
    items_with_ids = supabase.table('transaction_items_blaze') \
        .select('product_id, product_name') \
        .not_.is_('product_id', 'null') \
        .limit(10) \
        .execute()
    
    print(f"  Checking {len(items_with_ids.data)} sample items...")
    
    linked_count = 0
    unlinked_count = 0
    
    for item in items_with_ids.data:
        product_id = item.get('product_id')
        if product_id:
            # Try to find in products_blaze
            prod_result = supabase.table('products_blaze') \
                .select('product_id, name') \
                .eq('product_id', product_id) \
                .limit(1) \
                .execute()
            
            if prod_result.data:
                linked_count += 1
            else:
                unlinked_count += 1
                print(f"    UNLINKED: {item.get('product_name')} (ID: {product_id})")
    
    print(f"\n  Results:")
    print(f"    Linked to products_blaze:   {linked_count}")
    print(f"    NOT linked (orphaned):      {unlinked_count}")
    
    if unlinked_count > 0:
        print(f"\n  WARNING: {unlinked_count} items cannot be linked to products!")
        print("  This suggests products_blaze was cleared/nuked.")

except Exception as e:
    print(f"  ERROR: {e}")

print()

# 5. Check transactions
print("5. TRANSACTIONS CHECK")
print("-" * 80)

try:
    # Total transactions
    trans_result = supabase.table('transactions_blaze').select('*', count='exact').limit(0).execute()
    print(f"  Total transactions: {trans_result.count:,}")
    
    # Transactions with items
    items_per_trans = supabase.rpc('count_transaction_items', {}).execute() if False else None
    
    # Recent transactions
    print("\n  Recent transactions:")
    recent = supabase.table('transactions_blaze') \
        .select('transaction_id, date, total_amount, blaze_status') \
        .order('date', desc=True) \
        .limit(5) \
        .execute()
    
    for trans in recent.data:
        # Count items for this transaction
        items_count = supabase.table('transaction_items_blaze') \
            .select('*', count='exact') \
            .eq('transaction_id', trans['transaction_id']) \
            .limit(0) \
            .execute()
        
        print(f"    {trans['date'][:10]} | ${trans['total_amount']:.2f} | {items_count.count} items | {trans['blaze_status']}")

except Exception as e:
    print(f"  ERROR: {e}")

print()
print("=" * 80)
print("SUMMARY")
print("=" * 80)
print()
print("The CRM viewer (crm_integrated_blaze_v5.py) queries:")
print("  - transaction_items_blaze for product names and brands")
print("  - products_blaze is NOT currently used by the viewer")
print()
print("If transaction_items_blaze has product_name and brand populated,")
print("the viewer will work fine even if products_blaze was nuked.")
print()
print("Recommendations:")
print("  1. If products_blaze is empty, re-sync from Blaze API")
print("  2. Verify transaction_items have product_name populated")
print("  3. Consider linking items to products_blaze for enriched data")
print()
print("=" * 80)

