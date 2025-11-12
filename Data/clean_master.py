#!/usr/bin/env python3
"""
Clean up the MASTER CSV - fix product names that are actually reference numbers
"""

import pandas as pd
import re

df = pd.read_csv('mota_products_MASTER.csv')

print("Cleaning product names...")
print(f"Before: {len(df)} products\n")

cleaned_products = []

for idx, row in df.iterrows():
    product_name = row['product_name']
    strain_1 = row['strain_1']
    strain_2 = row['strain_2']
    
    # If product name is just a number or looks like a reference, use strain_1
    if re.match(r'^\d+\.?\d*$', str(product_name)) or product_name in ['MOTA Con DESCRIPTIONS', 'shorter', 'PM']:
        # Use strain_1 as the actual product name
        if pd.notna(strain_1) and str(strain_1).strip():
            print(f"  Fixing: '{product_name}' -> '{strain_1}'")
            row['product_name'] = strain_1
            # Shift strains
            row['strain_1'] = strain_2 if pd.notna(strain_2) else ''
            row['strain_2'] = row['strain_3'] if pd.notna(row['strain_3']) else ''
            row['strain_3'] = ''
    
    # Clean up effects - remove line breaks
    if pd.notna(row['effects']):
        effects = str(row['effects'])
        # Replace line breaks with spaces
        effects = effects.replace('\n', ' ').replace('\r', ' ')
        # Clean up multiple spaces
        effects = re.sub(r'\s+', ' ', effects)
        # Clean up bullet points
        effects = effects.replace('.', ',').strip()
        row['effects'] = effects
    
    cleaned_products.append(row)

df_cleaned = pd.DataFrame(cleaned_products)

# Remove products with no real name
df_cleaned = df_cleaned[df_cleaned['product_name'].notna()]
df_cleaned = df_cleaned[df_cleaned['product_name'] != '']

# Save
df_cleaned.to_csv('mota_products_CLEAN.csv', index=False)

print(f"\nAfter: {len(df_cleaned)} products")
print(f"\nSaved to: mota_products_CLEAN.csv")

# Show breakdown
print("\nBreakdown by category:")
for cat in df_cleaned['category'].unique():
    count = len(df_cleaned[df_cleaned['category'] == cat])
    print(f"  {cat}: {count} products")

# Show sample
print("\nSample products:")
for cat in df_cleaned['category'].unique():
    sample = df_cleaned[df_cleaned['category'] == cat].iloc[0]
    print(f"  [{cat}] {sample['product_name']}")
    if sample['strain_1']:
        print(f"    Strains: {sample['strain_1']} + {sample['strain_2']}")

