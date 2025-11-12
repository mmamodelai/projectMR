#!/usr/bin/env python3
"""
Import transaction items (line items) from CSV - FIXED VERSION
Uses column names instead of numeric indices to avoid misalignment
"""

import pandas as pd
from supabase import create_client, Client

# Supabase credentials
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

def main(test_mode=False, test_rows=1000):
    """Import transaction items from CSV"""
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    print("=" * 100)
    if test_mode:
        print(f"TESTING TRANSACTION ITEMS IMPORT (First {test_rows:,} rows)".center(100))
    else:
        print("IMPORTING TRANSACTION ITEMS - FULL IMPORT".center(100))
    print("=" * 100)
    
    # Read CSV - NO skiprows, use the actual header
    print("\nLoading CSV...")
    df = pd.read_csv('total_sales_products.csv', encoding='latin-1')
    
    if test_mode:
        df = df.head(test_rows)
        print(f"Loaded {len(df):,} rows for TESTING")
    else:
        print(f"Loaded {len(df):,} transaction line items")
    
    print(f"\nColumns available: {list(df.columns)[:10]}...")
    
    # Process transaction items
    print("\nProcessing transaction items...")
    transaction_items = []
    skipped = 0
    
    for idx, row in df.iterrows():
        if (idx + 1) % 10000 == 0:
            print(f"  Processing row {idx + 1:,}...")
        
        try:
            # Use COLUMN NAMES, not indices
            transaction_id = str(row['Trans No']) if pd.notna(row['Trans No']) else None
            product_name = str(row['Product']) if pd.notna(row['Product']) else None
            product_sku = str(row['SKU']) if pd.notna(row['SKU']) else None
            category = str(row['Product Category']) if pd.notna(row['Product Category']) else None
            strain = str(row['Flower Type']) if pd.notna(row['Flower Type']) else None
            flower_type = str(row['Flower Type']) if pd.notna(row['Flower Type']) else None
            brand = str(row['Brand']) if pd.notna(row['Brand']) else None
            
            # CRITICAL: Use correct price columns
            quantity = int(row['Quantity Sold']) if pd.notna(row['Quantity Sold']) and row['Quantity Sold'] > 0 else 1
            unit_price = float(row['Retail Price']) if pd.notna(row['Retail Price']) and row['Retail Price'] > 0 else 0.0
            
            # Calculate total price correctly
            total_price = unit_price * quantity
            
            # THC/CBD content
            thc_content = float(row['Total THC %']) if pd.notna(row['Total THC %']) else 0.0
            cbd_content = float(row['Total CBD %']) if pd.notna(row['Total CBD %']) else 0.0
            
            if not transaction_id or not product_name:
                skipped += 1
                continue
            
            item = {
                'transaction_id': int(transaction_id),
                'product_sku': product_sku,
                'product_name': product_name,
                'brand': brand,
                'category': category,
                'strain': strain,
                'flower_type': flower_type,
                'quantity': quantity,
                'unit_price': unit_price,
                'total_price': total_price,
                'thc_content': thc_content,
                'cbd_content': cbd_content
            }
            transaction_items.append(item)
            
        except Exception as e:
            skipped += 1
            if skipped <= 10:  # Show first 10 errors
                print(f"    WARNING Row {idx+1}: {str(e)}")
            continue
    
    print(f"\nPrepared {len(transaction_items):,} transaction items (skipped {skipped:,} invalid rows)")
    
    # Import in batches
    print(f"\nImporting transaction items in batches of 500...")
    batch_size = 500
    total_imported = 0
    errors = 0
    
    for i in range(0, len(transaction_items), batch_size):
        batch = transaction_items[i:i+batch_size]
        try:
            # Use regular insert (table has no unique constraint for duplicates)
            response = supabase.table('transaction_items').insert(batch).execute()
            total_imported += len(batch)
            if (i + batch_size) % 5000 == 0 or i == 0:
                print(f"  Imported {total_imported:,} items...")
        except Exception as e:
            errors += 1
            if errors <= 5:  # Show first 5 batch errors
                print(f"  ERROR in batch {i//batch_size + 1}: {str(e)[:100]}...")
    
    print(f"\nTransaction items imported: {total_imported:,}")
    if errors > 0:
        print(f"WARNING: Errors encountered: {errors} batches failed")
    
    # Verify
    print("\n" + "=" * 100)
    print("VERIFICATION")
    print("=" * 100)
    
    try:
        # Check transaction items count
        count_response = supabase.table('transaction_items').select('id', count='exact').limit(1).execute()
        print(f"Total transaction items in DB: {count_response.count:,}")
        
        # Check transaction 569043 specifically
        print("\nChecking Transaction 569043 (should have 2 items, not 4):")
        items_569043 = supabase.table('transaction_items').select('*').eq('transaction_id', 569043).execute()
        print(f"  Items found: {len(items_569043.data)}")
        
        item_total = 0
        for item in items_569043.data:
            subtotal = float(item['unit_price']) * int(item['quantity'])
            item_total += subtotal
            print(f"    - {item['product_name'][:50]}: ${item['unit_price']:.2f} x {item['quantity']} = ${subtotal:.2f}")
        
        print(f"  Items total: ${item_total:.2f} (should be ~$18.11)")
        
        if len(items_569043.data) == 2 and 17.0 < item_total < 19.0:
            print("\nSUCCESS! Transaction 569043 is CORRECT now!")
        else:
            print("\nWARNING: Transaction 569043 still has issues")
        
    except Exception as e:
        print(f"Verification error: {str(e)}")
    
    print("\n" + "=" * 100)
    if test_mode:
        print("TEST COMPLETE - Review results above before full import")
    else:
        print("DONE! Transaction items imported")
    print("=" * 100)

if __name__ == "__main__":
    import sys
    
    # Check if test mode
    test_mode = '--test' in sys.argv or '-t' in sys.argv
    
    if test_mode:
        print("\nRUNNING IN TEST MODE (1000 rows)")
        main(test_mode=True, test_rows=1000)
    else:
        print("\nFULL IMPORT MODE")
        confirm = input("This will import ALL rows. Type 'YES' to continue: ")
        if confirm == 'YES':
            main(test_mode=False)
        else:
            print("Aborted.")

