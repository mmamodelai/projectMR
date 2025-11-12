#!/usr/bin/env python3
"""
Leafly → Supabase Import Script
Fuzzy matches Leafly strain data to products and updates Supabase

Usage:
    python import_leafly_to_supabase.py
"""

import json
import re
import os
import sys
from datetime import datetime
from typing import List, Dict, Tuple
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

# File paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LEAFLY_JSON_PATH = os.path.join(PROJECT_ROOT, "Data", "inventory_enhanced_v2.json")


def normalize_strain_name(name: str) -> str:
    """
    Normalize strain name for fuzzy matching
    Removes common words, quantities, and special characters
    """
    if not name:
        return ""
    
    name = name.lower().strip()
    
    # Remove common product words
    remove_words = [
        'flower', 'strain', 'cannabis', 'weed', 'premium', 'mota', 'brand',
        'flwr', 'cart', 'cartridge', 'pre-roll', 'preroll', 'vape', 'extract',
        'eighth', '8th', 'oz', 'gram', 'stiiizy', 'rawg', 'jeeter', 'kiva',
        'infused', 'live', 'resin', 'sugar', 'wax', 'shatter', 'diamond',
        'liquid', 'pod', 'airopro', 'pax', 'select', 'absolute', 'extract',
        'concentrate', 'disposable', 'rechargeable'
    ]
    
    for word in remove_words:
        name = re.sub(rf'\b{word}\b', '', name, flags=re.IGNORECASE)
    
    # Remove quantities (3.5g, 1oz, 100mg, .5g, 0.5g, 1g, etc.)
    name = re.sub(r'\d+\.?\d*\s*(g|gram|oz|ounce|mg|ml)s?', '', name, flags=re.IGNORECASE)
    
    # Remove strain types
    name = re.sub(r'\b(indica|sativa|hybrid|balanced|dominant)\b', '', name, flags=re.IGNORECASE)
    
    # Remove special characters and normalize
    name = name.replace('#', '').replace('-', ' ').replace('_', ' ')
    name = name.replace('&', 'and')
    
    # Remove multiple spaces
    name = re.sub(r'\s+', ' ', name)
    
    return name.strip()


def calculate_match_confidence(strain_name: str, product_name: str) -> int:
    """
    Calculate confidence score (0-100) for strain-product match
    
    Strategies:
    1. Exact normalized match: 100
    2. Strain name in product: 95
    3. Product name in strain: 90
    4. Word overlap: 60-85
    """
    norm_strain = normalize_strain_name(strain_name)
    norm_product = normalize_strain_name(product_name)
    
    if not norm_strain or not norm_product:
        return 0
    
    # Strategy 1: Exact match
    if norm_strain == norm_product:
        return 100
    
    # Strategy 2: Strain name appears in product name
    if norm_strain in norm_product:
        # Calculate how much of the product name is the strain
        overlap_ratio = len(norm_strain) / len(norm_product)
        return min(95, int(90 + (overlap_ratio * 10)))
    
    # Strategy 3: Product name appears in strain name
    if norm_product in norm_strain:
        overlap_ratio = len(norm_product) / len(norm_strain)
        return int(85 + (overlap_ratio * 5))
    
    # Strategy 4: Word overlap
    strain_words = set(norm_strain.split())
    product_words = set(norm_product.split())
    
    if not strain_words or not product_words:
        return 0
    
    # Remove single-letter words
    strain_words = {w for w in strain_words if len(w) > 1}
    product_words = {w for w in product_words if len(w) > 1}
    
    if not strain_words or not product_words:
        return 0
    
    common_words = strain_words & product_words
    
    if not common_words:
        return 0
    
    # Calculate overlap percentage
    overlap_pct = len(common_words) / min(len(strain_words), len(product_words))
    
    # Must have significant overlap
    if overlap_pct < 0.5:
        return 0
    
    return int(60 + (overlap_pct * 25))


def find_matching_products(strain_name: str, products: List[Dict]) -> List[Tuple[Dict, int]]:
    """
    Find products that match a strain name
    Returns list of (product, confidence_score) tuples
    """
    matches = []
    
    for product in products:
        product_name = product.get('name', '')
        if not product_name:
            continue
        
        confidence = calculate_match_confidence(strain_name, product_name)
        
        if confidence >= 85:  # Threshold for high-confidence match
            matches.append((product, confidence))
    
    # Sort by confidence (highest first)
    matches.sort(key=lambda x: x[1], reverse=True)
    
    return matches


def prepare_leafly_update(leafly_data: Dict) -> Dict:
    """
    Prepare Leafly data for Supabase update
    Converts Python objects to PostgreSQL-compatible formats
    """
    return {
        'leafly_strain_type': leafly_data.get('strain_type'),
        'leafly_description': leafly_data.get('description'),
        'leafly_rating': float(leafly_data['rating']) if leafly_data.get('rating') else None,
        'leafly_review_count': int(leafly_data['review_count']) if leafly_data.get('review_count') else None,
        'effects': leafly_data.get('effects', []),
        'helps_with': leafly_data.get('helps_with', []),
        'negatives': leafly_data.get('negatives', []),
        'flavors': leafly_data.get('flavors', []),
        'terpenes': leafly_data.get('terpenes', []),
        'parent_strains': leafly_data.get('parent_strains', []),
        'lineage': leafly_data.get('lineage'),
        'image_url': leafly_data.get('image_url'),
        'leafly_url': leafly_data.get('url'),
        'leafly_data_updated_at': datetime.now().isoformat()
    }


def main():
    """Main import process"""
    print("\n" + "="*80)
    print("LEAFLY → SUPABASE IMPORT")
    print("="*80 + "\n")
    
    # 1. Load Leafly data
    print(f"📄 Loading Leafly data from: {LEAFLY_JSON_PATH}")
    try:
        with open(LEAFLY_JSON_PATH, 'r', encoding='utf-8') as f:
            leafly_strains = json.load(f)
        print(f"✅ Loaded {len(leafly_strains)} strains\n")
    except FileNotFoundError:
        print(f"❌ ERROR: File not found: {LEAFLY_JSON_PATH}")
        return 1
    except json.JSONDecodeError as e:
        print(f"❌ ERROR: Invalid JSON: {e}")
        return 1
    
    # 2. Connect to Supabase
    print("🔌 Connecting to Supabase...")
    if not SUPABASE_KEY:
        print("❌ ERROR: SUPABASE_SERVICE_ROLE_KEY environment variable not set!")
        print("\nSet it with:")
        print("  $env:SUPABASE_SERVICE_ROLE_KEY='your-key-here'  # PowerShell")
        print("  export SUPABASE_SERVICE_ROLE_KEY='your-key-here'  # Bash")
        return 1
    
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Connected to Supabase\n")
    except Exception as e:
        print(f"❌ ERROR: Failed to connect to Supabase: {e}")
        return 1
    
    # 3. Fetch all products
    print("📦 Fetching products from Supabase...")
    try:
        response = supabase.table('products').select('id,product_id,name,category,strain').execute()
        products = response.data
        print(f"✅ Total products: {len(products):,}\n")
    except Exception as e:
        print(f"❌ ERROR: Failed to fetch products: {e}")
        return 1
    
    # 4. Match and update
    print("🔗 Matching strains to products...\n")
    print("="*80 + "\n")
    
    total_matches = 0
    total_updated = 0
    total_errors = 0
    
    for idx, leafly_strain in enumerate(leafly_strains, 1):
        strain_name = leafly_strain['name']
        print(f"[{idx}/{len(leafly_strains)}] {strain_name}")
        print("-" * 80)
        
        # Find matching products
        matches = find_matching_products(strain_name, products)
        
        if not matches:
            print(f"  ⚠️  No matches found (need 85%+ confidence)\n")
            continue
        
        print(f"  ✅ Found {len(matches)} match(es):")
        
        # Show top 3 examples
        for product, confidence in matches[:3]:
            print(f"     • [{confidence}%] {product['name'][:60]}")
        
        if len(matches) > 3:
            print(f"     ... and {len(matches) - 3} more")
        
        print(f"\n  📝 Updating {len(matches)} product(s)...")
        
        # Prepare update data
        update_data = prepare_leafly_update(leafly_strain)
        
        # Update all matching products
        updated_count = 0
        error_count = 0
        
        for product, confidence in matches:
            try:
                supabase.table('products').update(update_data).eq('id', product['id']).execute()
                updated_count += 1
                total_updated += 1
            except Exception as e:
                print(f"     ❌ Error updating {product['name']}: {e}")
                error_count += 1
                total_errors += 1
        
        if updated_count > 0:
            print(f"     ✅ Updated: {updated_count} products")
        if error_count > 0:
            print(f"     ❌ Errors: {error_count} products")
        
        total_matches += len(matches)
        print()
    
    # 5. Final summary
    print("="*80)
    print("IMPORT COMPLETE")
    print("="*80)
    print(f"Strains processed:    {len(leafly_strains)}")
    print(f"Matches found:        {total_matches:,}")
    print(f"Products updated:     {total_updated:,}")
    print(f"Update errors:        {total_errors}")
    print("="*80 + "\n")
    
    # 6. Verify results
    print("✅ Verifying results...\n")
    try:
        verify_response = supabase.table('products').select('id', count='exact').not_.is_('leafly_description', 'null').execute()
        products_with_leafly = verify_response.count if hasattr(verify_response, 'count') else len(verify_response.data)
        print(f"Products with Leafly data: {products_with_leafly:,}\n")
    except Exception as e:
        print(f"⚠️  Could not verify: {e}\n")
    
    print("✨ Import complete! Check Supabase for updated data.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())



