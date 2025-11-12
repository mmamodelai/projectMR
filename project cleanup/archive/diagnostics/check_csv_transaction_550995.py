#!/usr/bin/env python3
"""
Check CSV for transaction 550995
"""

import pandas as pd

df = pd.read_csv('total_sales_products.csv', skiprows=1, encoding='latin-1')

# Filter for transaction 550995 (column 4 = Trans No)
trans = df[df.iloc[:, 4].astype(str) == '550995']

print("=" * 80)
print("TRANSACTION 550995 IN CSV FILE")
print("=" * 80)
print(f"Total rows found: {len(trans)}")
print()

if len(trans) == 0:
    print("Transaction not found in CSV!")
    exit(1)

print("ITEMS IN CSV:")
print("=" * 80)

total_csv = 0
for i, (idx, row) in enumerate(trans.iterrows(), 1):
    product = row.iloc[5]  # Product Name
    total_price = float(row.iloc[27]) if pd.notna(row.iloc[27]) else 0  # Total Price
    qty = row.iloc[17] if pd.notna(row.iloc[17]) else 0  # Qty Sold
    
    print(f"{i}. {product}")
    print(f"   Total Price: ${total_price:.2f}")
    print(f"   Qty: {qty}")
    print()
    
    total_csv += total_price

print("=" * 80)
print(f"Sum of all items in CSV: ${total_csv:.2f}")
print("=" * 80)

