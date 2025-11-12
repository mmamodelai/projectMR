#!/usr/bin/env python3
"""
Fix Inventory Viewer issues and enhance product data
"""

import pandas as pd
from supabase import create_client, Client
import re

# Supabase credentials
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

def extract_thc_cbd_from_name(product_name):
    """Extract THC/CBD percentages from product names"""
    if not product_name or product_name == 'Unknown':
        return None, None
    
    # Common patterns for THC/CBD in product names
    thc_patterns = [
        r'(\d+(?:\.\d+)?)\s*mg\s*THC',  # "100mg THC"
        r'(\d+(?:\.\d+)?)\s*%\s*THC',   # "25% THC"
        r'THC[:\s]*(\d+(?:\.\d+)?)',    # "THC: 100" or "THC 100"
        r'(\d+(?:\.\d+)?)\s*mg',       # "100mg" (assume THC if no CBD)
    ]
    
    cbd_patterns = [
        r'(\d+(?:\.\d+)?)\s*mg\s*CBD',  # "10mg CBD"
        r'(\d+(?:\.\d+)?)\s*%\s*CBD',   # "5% CBD"
        r'CBD[:\s]*(\d+(?:\.\d+)?)',    # "CBD: 10" or "CBD 10"
    ]
    
    thc_content = None
    cbd_content = None
    
    # Extract THC
    for pattern in thc_patterns:
        match = re.search(pattern, product_name, re.IGNORECASE)
        if match:
            try:
                thc_content = float(match.group(1))
                break
            except:
                continue
    
    # Extract CBD
    for pattern in cbd_patterns:
        match = re.search(pattern, product_name, re.IGNORECASE)
        if match:
            try:
                cbd_content = float(match.group(1))
                break
            except:
                continue
    
    return thc_content, cbd_content

def categorize_product(product_name, category):
    """Better categorize products based on name and existing category"""
    if not product_name or product_name == 'Unknown':
        return 'Unknown'
    
    name_lower = product_name.lower()
    
    # Flower/Pre-rolls
    if any(word in name_lower for word in ['flower', 'pre-roll', 'preroll', 'joint', 'blunt']):
        return 'Flower'
    
    # Vapes
    if any(word in name_lower for word in ['vape', 'cart', 'cartridge', 'aio', 'disposable']):
        return 'Vapes'
    
    # Edibles
    if any(word in name_lower for word in ['gummy', 'gummies', 'chocolate', 'cookie', 'brownie', 'edible', 'beverage', 'drink']):
        return 'Edibles'
    
    # Concentrates
    if any(word in name_lower for word in ['wax', 'shatter', 'rosin', 'live resin', 'badder', 'crumble', 'sauce']):
        return 'Concentrates'
    
    # Topicals/CBD
    if any(word in name_lower for word in ['balm', 'cream', 'lotion', 'topical', 'cbd']):
        return 'Topicals'
    
    # Accessories
    if any(word in name_lower for word in ['grinder', 'pipe', 'bong', 'vaporizer', 'battery', 'charger']):
        return 'Accessories'
    
    # Fees/Services
    if any(word in name_lower for word in ['recycling', 'fee', 'service', 'deposit']):
        return 'Fees'
    
    # Use existing category if it's not generic
    if category and category not in ['REGULAR', 'Unknown', 'N/A']:
        return category
    
    return 'Other'

def main():
    """Fix inventory viewer issues"""
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    print("=" * 70)
    print("FIXING INVENTORY VIEWER ISSUES".center(70))
    print("=" * 70)
    
    # Get all products
    print("\nLoading products from database...")
    response = supabase.table('products').select('*').execute()
    products = response.data
    print(f"Loaded {len(products)} products")
    
    # Process products
    print("\nProcessing products...")
    updates = []
    
    for i, product in enumerate(products):
        if (i + 1) % 1000 == 0:
            print(f"  Processing product {i + 1:,}...")
        
        product_name = product.get('name', '')
        current_category = product.get('category', '')
        
        # Extract THC/CBD from product name
        thc_content, cbd_content = extract_thc_cbd_from_name(product_name)
        
        # Better categorize
        new_category = categorize_product(product_name, current_category)
        
        # Prepare update
        update_data = {}
        
        if thc_content is not None:
            update_data['thc_content'] = thc_content
        if cbd_content is not None:
            update_data['cbd_content'] = cbd_content
        if new_category != current_category:
            update_data['category'] = new_category
        
        if update_data:
            update_data['id'] = product['id']
            updates.append(update_data)
    
    print(f"Prepared {len(updates)} product updates")
    
    # Update products in batches
    if updates:
        print(f"\nUpdating products in batches of 100...")
        batch_size = 100
        total_updated = 0
        
        for i in range(0, len(updates), batch_size):
            batch = updates[i:i+batch_size]
            
            for update in batch:
                try:
                    product_id = update.pop('id')
                    supabase.table('products').update(update).eq('id', product_id).execute()
                    total_updated += 1
                except Exception as e:
                    print(f"  Error updating product {product_id}: {str(e)[:50]}...")
            
            if (i + batch_size) % 1000 == 0:
                print(f"  Updated {total_updated:,} products...")
        
        print(f"Products updated: {total_updated:,}")
    
    # Verify results
    print("\n" + "=" * 70)
    print("VERIFICATION")
    print("=" * 70)
    
    try:
        # Check products with THC/CBD
        thc_count = supabase.table('products').select('id', count='exact').gt('thc_content', 0).execute()
        cbd_count = supabase.table('products').select('id', count='exact').gt('cbd_content', 0).execute()
        
        print(f"Products with THC content: {thc_count.count:,}")
        print(f"Products with CBD content: {cbd_count.count:,}")
        
        # Check categories
        category_response = supabase.table('products').select('category').execute()
        categories = {}
        for product in category_response.data:
            cat = product.get('category', 'Unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        print(f"\nProduct categories:")
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            print(f"  {cat}: {count:,}")
        
        # Sample products with THC/CBD
        sample_response = supabase.table('products').select('name, thc_content, cbd_content, category').gt('thc_content', 0).limit(5).execute()
        print(f"\nSample products with THC:")
        for product in sample_response.data:
            print(f"  {product['name'][:50]}... - THC: {product['thc_content']}%, CBD: {product['cbd_content']}%")
        
    except Exception as e:
        print(f"Verification error: {str(e)}")
    
    print("\n" + "=" * 70)
    print("DONE! Inventory Viewer should now show better data")
    print("=" * 70)

if __name__ == "__main__":
    main()
