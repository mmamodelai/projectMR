#!/usr/bin/env python3
"""
Import Leafly strain data into Supabase products table
Matches strain names with products and updates with rich data

Usage:
    python import_leafly_data.py

Requirements:
    pip install supabase fuzzywuzzy python-levenshtein

Data Source: ../Data/inventory_enhanced_v2.json (24 strains)
"""

import json
import re
import os
from pathlib import Path
from datetime import datetime
from supabase import create_client, Client
from fuzzywuzzy import fuzz

# ============================================================================
# Configuration
# ============================================================================

# Supabase connection (update these!)
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://kiwmwoqrguyrcpjytgte.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', 'your-service-role-key-here')

# Data file path
LEAFLY_DATA_PATH = '../Data/inventory_enhanced_v2.json'

# Matching thresholds
EXACT_MATCH_THRESHOLD = 100
HIGH_CONFIDENCE_THRESHOLD = 90
FUZZY_MATCH_THRESHOLD = 85

# ============================================================================
# Helper Functions
# ============================================================================

def normalize_strain_name(name):
    """
    Normalize strain name for matching
    
    Examples:
        "MOTA - Gelato #41 - 3.5g" -> "gelato 41"
        "Ice Cream Cake Flower" -> "ice cream cake"
        "Green Crack (Sativa)" -> "green crack"
    """
    if not name:
        return ""
    
    name = str(name).lower().strip()
    
    # Remove common words
    remove_words = ['flower', 'strain', 'cannabis', 'weed', 'premium', 'mota', 'brand']
    for word in remove_words:
        name = re.sub(rf'\b{word}\b', '', name)
    
    # Remove quantities (3.5g, 1oz, 100mg)
    name = re.sub(r'\d+\.?\d*\s*(g|gram|oz|ounce|mg|milligram)s?', '', name)
    
    # Remove parentheticals like (Sativa), (Indica)
    name = re.sub(r'\([^)]*\)', '', name)
    
    # Normalize special characters
    name = name.replace('#', '').replace('-', ' ').replace('_', ' ')
    
    # Remove multiple spaces
    name = re.sub(r'\s+', ' ', name)
    
    return name.strip()


def match_strain_to_products(strain_name, products):
    """
    Match strain name to products using multi-strategy matching
    
    Returns:
        List of (product, confidence_score) tuples, sorted by confidence
    """
    matches = []
    normalized_strain = normalize_strain_name(strain_name)
    
    for product in products:
        product_name = product.get('name', '')
        normalized_product = normalize_strain_name(product_name)
        
        # Skip if no name
        if not normalized_product:
            continue
        
        # Strategy 1: Exact match
        if normalized_strain == normalized_product:
            matches.append((product, EXACT_MATCH_THRESHOLD))
            continue
        
        # Strategy 2: Contains match (strain name in product name)
        if normalized_strain in normalized_product:
            matches.append((product, HIGH_CONFIDENCE_THRESHOLD))
            continue
        
        # Strategy 3: Fuzzy match
        similarity = fuzz.ratio(normalized_strain, normalized_product)
        if similarity >= FUZZY_MATCH_THRESHOLD:
            matches.append((product, similarity))
    
    # Sort by confidence (highest first)
    matches.sort(key=lambda x: x[1], reverse=True)
    return matches


def prepare_update_data(strain):
    """Prepare Leafly data for Supabase update"""
    return {
        'leafly_strain_type': strain.get('strain_type'),
        'leafly_description': strain.get('description'),
        'leafly_rating': float(strain.get('rating', 0)) if strain.get('rating') else None,
        'leafly_review_count': strain.get('review_count', 0),
        'effects': strain.get('effects', []) or [],
        'helps_with': strain.get('helps_with', []) or [],
        'negatives': strain.get('negatives', []) or [],
        'flavors': strain.get('flavors', []) or [],
        'terpenes': strain.get('terpenes', []) or [],
        'parent_strains': strain.get('parent_strains', []) or [],
        'lineage': strain.get('lineage'),
        'image_url': strain.get('image_url'),
        'leafly_url': strain.get('url'),
        'leafly_data_updated_at': datetime.now().isoformat()
    }


# ============================================================================
# Main Import Function
# ============================================================================

def import_leafly_data():
    """Main import function"""
    
    print("="*80)
    print("LEAFLY DATA IMPORT TO SUPABASE")
    print("="*80)
    
    # 1. Load Leafly data
    print(f"\n📄 Loading Leafly data from: {LEAFLY_DATA_PATH}")
    leafly_path = Path(__file__).parent / LEAFLY_DATA_PATH
    
    if not leafly_path.exists():
        print(f"❌ Error: File not found: {leafly_path}")
        return 1
    
    with open(leafly_path, 'r', encoding='utf-8') as f:
        leafly_data = json.load(f)
    
    print(f"✅ Loaded {len(leafly_data)} strains")
    
    # 2. Connect to Supabase
    print(f"\n🔌 Connecting to Supabase...")
    
    if SUPABASE_KEY == 'your-service-role-key-here':
        print("❌ Error: Please update SUPABASE_KEY in the script")
        print("   Get it from: Supabase Dashboard > Project Settings > API > service_role key")
        return 1
    
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Connected to Supabase")
    except Exception as e:
        print(f"❌ Error connecting to Supabase: {e}")
        return 1
    
    # 3. Fetch all products
    print(f"\n📦 Fetching products from Supabase...")
    products = []
    page_size = 1000
    offset = 0
    
    try:
        while True:
            response = supabase.table('products').select('id, product_id, name, category').range(offset, offset + page_size - 1).execute()
            if not response.data:
                break
            products.extend(response.data)
            offset += page_size
            print(f"   Fetched {len(products)} products...")
        
        print(f"✅ Total products: {len(products)}")
    except Exception as e:
        print(f"❌ Error fetching products: {e}")
        return 1
    
    # 4. Match and update
    print(f"\n🔗 Matching strains to products...")
    print("="*80)
    
    stats = {
        'strains_processed': 0,
        'matches_found': 0,
        'products_updated': 0,
        'update_errors': 0
    }
    
    for strain in leafly_data:
        stats['strains_processed'] += 1
        strain_name = strain['name']
        
        print(f"\n[{stats['strains_processed']}/{len(leafly_data)}] {strain_name}")
        print("-" * 80)
        
        # Find matching products
        matches = match_strain_to_products(strain_name, products)
        
        if not matches:
            print("  ❌ No matches found")
            continue
        
        # Show all matches
        print(f"  ✅ Found {len(matches)} match(es):")
        for i, (product, confidence) in enumerate(matches[:5], 1):  # Show top 5
            print(f"     {i}. [{confidence}%] {product['name']}")
        
        # Filter high-confidence matches
        high_confidence = [m for m in matches if m[1] >= FUZZY_MATCH_THRESHOLD]
        stats['matches_found'] += len(high_confidence)
        
        if not high_confidence:
            print(f"  ⚠️  No high-confidence matches (threshold: {FUZZY_MATCH_THRESHOLD}%)")
            continue
        
        # Update all high-confidence matches
        update_data = prepare_update_data(strain)
        
        print(f"\n  📝 Updating {len(high_confidence)} product(s)...")
        
        for product, confidence in high_confidence:
            try:
                supabase.table('products').update(update_data).eq('id', product['id']).execute()
                stats['products_updated'] += 1
                print(f"     ✅ Updated: {product['name']}")
            except Exception as e:
                stats['update_errors'] += 1
                print(f"     ❌ Error: {e}")
    
    # 5. Summary
    print("\n" + "="*80)
    print("IMPORT COMPLETE")
    print("="*80)
    print(f"Strains processed:    {stats['strains_processed']}")
    print(f"Matches found:        {stats['matches_found']}")
    print(f"Products updated:     {stats['products_updated']}")
    print(f"Update errors:        {stats['update_errors']}")
    print("="*80)
    
    # 6. Verification query
    print("\n📊 Verifying import...")
    try:
        result = supabase.table('products').select('id', count='exact').not_.is_('leafly_description', 'null').execute()
        count = result.count
        print(f"✅ Products with Leafly data: {count}")
    except Exception as e:
        print(f"❌ Verification error: {e}")
    
    print("\n✅ Done!")
    return 0


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import sys
    
    # Check dependencies
    try:
        import fuzzywuzzy
        from supabase import create_client
    except ImportError:
        print("❌ Error: Missing dependencies")
        print("   Run: pip install supabase fuzzywuzzy python-levenshtein")
        sys.exit(1)
    
    # Run import
    sys.exit(import_leafly_data())



