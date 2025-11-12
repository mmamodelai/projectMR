#!/usr/bin/env python3
"""
Import unique products from the transaction CSV into the products table
"""

import pandas as pd
from supabase import create_client, Client

# Supabase credentials
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

def import_products():
    """Import unique products from CSV"""
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    print("=" * 60)
    print("MoTa Product Import from Transaction CSV".center(60))
    print("=" * 60)
    
    try:
        # Read CSV
        print("Loading transaction CSV...")
        df = pd.read_csv('total_sales_products.csv', skiprows=1, encoding='latin-1')
        print(f"Loaded {len(df)} transaction line items")
        
        # Extract unique products
        print("\nExtracting unique products...")
        products = {}
        
        for idx, row in df.iterrows():
            if (idx + 1) % 5000 == 0:
                print(f"  Processed {idx + 1:,} rows...")
            
            # Extract product data
            product_sku = str(row.iloc[11]) if pd.notna(row.iloc[11]) else None  # Product ID
            product_name = str(row.iloc[10]) if pd.notna(row.iloc[10]) else None  # Product Name
            brand = str(row.iloc[16]) if pd.notna(row.iloc[16]) else None  # Brand
            category = str(row.iloc[14]) if pd.notna(row.iloc[14]) else None  # Category
            strain = str(row.iloc[13]) if pd.notna(row.iloc[13]) else None  # Strain/Type
            flower_type = str(row.iloc[15]) if pd.notna(row.iloc[15]) else None  # Flower Type
            
            # Skip if no product name
            if not product_name or product_name == 'nan':
                continue
            
            # Create unique key
            key = f"{product_name}_{brand}"
            
            if key not in products:
                products[key] = {
                    'product_id': product_sku,
                    'name': product_name,
                    'brand': brand,
                    'category': category,
                    'flower_type': flower_type,
                    'strain': strain,
                    'vendor': brand,  # Use brand as vendor for now
                    'is_active': True
                }
        
        print(f"\nFound {len(products)} unique products")
        
        # Convert to list for batch insert
        product_list = list(products.values())
        
        # Insert products in batches
        batch_size = 500
        total_imported = 0
        
        print(f"\nImporting products in batches of {batch_size}...")
        for i in range(0, len(product_list), batch_size):
            batch = product_list[i:i+batch_size]
            batch_num = i // batch_size + 1
            total_batches = (len(product_list) - 1) // batch_size + 1
            
            try:
                response = supabase.table('products').insert(batch).execute()
                total_imported += len(batch)
                print(f"  Batch {batch_num}/{total_batches}: Imported {len(batch)} products (Total: {total_imported:,})")
            except Exception as e:
                print(f"  Batch {batch_num}/{total_batches}: ERROR - {str(e)[:100]}...")
        
        print("\n" + "=" * 60)
        print(f"Product Import Complete!")
        print(f"  Total products imported: {total_imported:,}")
        
        # Verify final count
        print("\nVerifying database...")
        final_count = supabase.table('products').select('product_id', count='exact').execute()
        print(f"  Total products in database: {final_count.count:,}")
        
        print("=" * 60)
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    import_products()

