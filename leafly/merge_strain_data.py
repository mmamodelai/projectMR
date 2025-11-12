#!/usr/bin/env python3
"""
Merge Leafly scraped data with existing product database
Updates product descriptions, effects, and terpene profiles

Usage:
    python merge_strain_data.py leafly_strains.json mota_products_FINAL.csv
"""

import sys
import json
import pandas as pd
import argparse
from pathlib import Path


def load_leafly_data(json_file: str) -> pd.DataFrame:
    """Load scraped Leafly data from JSON"""
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Flatten list columns to comma-separated strings
    for col in ['effects', 'flavors', 'terpenes', 'parent_strains']:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: ', '.join(x) if isinstance(x, list) else '')
    
    return df


def normalize_strain_name(name: str) -> str:
    """Normalize strain name for matching"""
    if pd.isna(name):
        return ''
    
    name = str(name).lower().strip()
    # Remove special characters
    name = name.replace('#', '').replace('  ', ' ')
    return name


def merge_data(products_df: pd.DataFrame, leafly_df: pd.DataFrame) -> pd.DataFrame:
    """Merge Leafly data with product database"""
    
    # Normalize names for matching
    products_df['_normalized_name'] = products_df['product_name'].apply(normalize_strain_name)
    leafly_df['_normalized_name'] = leafly_df['name'].apply(normalize_strain_name)
    
    # Merge on normalized name
    merged = products_df.merge(
        leafly_df[['_normalized_name', 'description', 'effects', 'flavors', 'terpenes', 
                   'thc_percent', 'cbd_percent', 'strain_type', 'rating', 'parent_strains']],
        on='_normalized_name',
        how='left',
        suffixes=('', '_leafly')
    )
    
    # Update fields where Leafly has data
    update_fields = {
        'gpt_description': 'description',
        'effects': 'effects',
        'strain_type': 'strain_type',
    }
    
    for prod_col, leafly_col in update_fields.items():
        if prod_col in merged.columns and leafly_col in merged.columns:
            # Update only if Leafly has data and product doesn't
            mask = merged[leafly_col].notna() & (merged[prod_col].isna() | (merged[prod_col] == ''))
            merged.loc[mask, prod_col] = merged.loc[mask, leafly_col]
    
    # Add new columns if they don't exist
    new_columns = {
        'leafly_flavors': 'flavors',
        'leafly_terpenes': 'terpenes',
        'leafly_rating': 'rating',
        'leafly_lineage': 'parent_strains',
    }
    
    for new_col, leafly_col in new_columns.items():
        if leafly_col in merged.columns:
            merged[new_col] = merged[leafly_col]
    
    # Remove temporary columns
    merged = merged.drop(columns=['_normalized_name'] + 
                        [col for col in merged.columns if col.endswith('_leafly')])
    
    return merged


def generate_report(original_df: pd.DataFrame, merged_df: pd.DataFrame) -> dict:
    """Generate merge statistics report"""
    
    report = {
        'total_products': len(original_df),
        'products_enhanced': 0,
        'descriptions_added': 0,
        'effects_added': 0,
        'terpenes_added': 0,
    }
    
    # Count enhancements
    if 'gpt_description' in merged_df.columns:
        orig_desc_count = original_df['gpt_description'].notna().sum()
        new_desc_count = merged_df['gpt_description'].notna().sum()
        report['descriptions_added'] = new_desc_count - orig_desc_count
    
    if 'leafly_terpenes' in merged_df.columns:
        report['terpenes_added'] = merged_df['leafly_terpenes'].notna().sum()
    
    if 'leafly_flavors' in merged_df.columns:
        report['products_enhanced'] = merged_df['leafly_flavors'].notna().sum()
    
    return report


def main():
    parser = argparse.ArgumentParser(description='Merge Leafly data with product database')
    parser.add_argument('leafly_json', help='Path to Leafly scraped JSON file')
    parser.add_argument('products_csv', help='Path to products CSV file')
    parser.add_argument('--output', '-o', help='Output CSV file', default='mota_products_enhanced.csv')
    parser.add_argument('--report', help='Generate report file', action='store_true')
    
    args = parser.parse_args()
    
    # Check files exist
    if not Path(args.leafly_json).exists():
        print(f"❌ Error: {args.leafly_json} not found")
        return 1
    
    if not Path(args.products_csv).exists():
        print(f"❌ Error: {args.products_csv} not found")
        return 1
    
    print("🔄 Loading data...")
    
    # Load data
    try:
        leafly_df = load_leafly_data(args.leafly_json)
        products_df = pd.read_csv(args.products_csv)
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return 1
    
    print(f"   Leafly strains: {len(leafly_df)}")
    print(f"   Products: {len(products_df)}")
    
    print("\n🔗 Merging data...")
    
    # Merge
    try:
        merged_df = merge_data(products_df, leafly_df)
    except Exception as e:
        print(f"❌ Error merging data: {e}")
        return 1
    
    # Generate report
    report = generate_report(products_df, merged_df)
    
    print("\n📊 Merge Report:")
    print(f"   Total products: {report['total_products']}")
    print(f"   Products enhanced: {report['products_enhanced']}")
    print(f"   Descriptions added: {report['descriptions_added']}")
    print(f"   Terpene profiles added: {report['terpenes_added']}")
    
    # Save merged data
    print(f"\n💾 Saving to {args.output}...")
    try:
        merged_df.to_csv(args.output, index=False)
        print(f"✅ Successfully saved {len(merged_df)} products")
    except Exception as e:
        print(f"❌ Error saving file: {e}")
        return 1
    
    # Save report if requested
    if args.report:
        report_file = args.output.replace('.csv', '_report.json')
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"📄 Report saved to {report_file}")
    
    print("\n✅ Merge complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())

