#!/usr/bin/env python3
"""
Analyze Aaron Campos purchase patterns
"""

import pandas as pd

df = pd.read_csv('total_sales_products.csv', skiprows=1, encoding='latin-1')
aaron_customer_id = '6344773b27c6ed59caa94626'
aaron_items = df[df.iloc[:, 19] == aaron_customer_id]

if len(aaron_items) > 0:
    print('AARON CAMPOS - DETAILED PURCHASE ANALYSIS')
    print('=' * 70)
    
    # Get unique transactions
    unique_trans = aaron_items.iloc[:, 4].nunique()
    total_items = len(aaron_items)
    avg_items_per_trans = total_items / unique_trans
    
    print(f'\nPurchase Patterns:')
    print(f'  Total transactions: {unique_trans}')
    print(f'  Total items purchased: {total_items}')
    print(f'  Average items per transaction: {avg_items_per_trans:.1f}')
    
    # Top products
    print(f'\nTop 10 Most Purchased Products:')
    product_counts = aaron_items.iloc[:, 10].value_counts().head(10)
    for idx, (product, count) in enumerate(product_counts.items(), 1):
        print(f'  {idx}. [{count}x] {product}')
    
    # Categories breakdown
    print(f'\nCategory Breakdown:')
    category_counts = aaron_items.iloc[:, 14].value_counts()
    for cat, count in category_counts.items():
        if pd.notna(cat) and cat != 'FEES':
            print(f'  {count} items - {cat}')
    
    # Strain preferences (Hybrid, Indica, Sativa)
    print(f'\nFlower Type Preferences:')
    strain_counts = aaron_items.iloc[:, 13].value_counts()
    for strain, count in strain_counts.items():
        if pd.notna(strain) and strain != '':
            print(f'  {count}x - {strain}')
    
    # Brand loyalty
    print(f'\nBrand Preferences:')
    brand_counts = aaron_items.iloc[:, 16].value_counts().head(5)
    for brand, count in brand_counts.items():
        if pd.notna(brand) and brand != 'STATEHOUSE':  # Skip generic
            print(f'  {count} items - {brand}')
    
    # Recent purchases
    print(f'\nMost Recent Purchases (Last 5 transactions):')
    recent = aaron_items.sort_values(by=aaron_items.columns[0], ascending=False).head(10)
    for _, row in recent.iterrows():
        date = row.iloc[0]
        product = row.iloc[10]
        print(f'  {date}: {product}')

print('\nCRM Viewer is now open - search for "Aaron Campos" to see full details!')

