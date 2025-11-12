#!/usr/bin/env python3
"""
Analyze CSV columns to understand the data structure
"""

import pandas as pd

df = pd.read_csv('total_sales_products.csv', skiprows=1, encoding='latin-1')

print("=" * 80)
print("CSV COLUMN STRUCTURE")
print("=" * 80)
for i, col in enumerate(df.columns):
    print(f"Col {i:2d}: {col}")

print("\n" + "=" * 80)
print("TRANSACTION 550995 - WHAT'S IN EACH COLUMN")
print("=" * 80)

trans = df[df.iloc[:, 4].astype(str) == '550995']

print(f"\nFound {len(trans)} rows for transaction 550995\n")

for idx, row in trans.iterrows():
    print(f"Row {idx}:")
    print(f"  Col 4 (Trans No): {row.iloc[4]}")
    print(f"  Col 5 (Product): {row.iloc[5]}")
    print(f"  Col 10 (script uses as product_name): {row.iloc[10]}")
    print(f"  Col 11 (script uses as product_sku): {row.iloc[11]}")
    print(f"  Col 12 (script uses as category): {row.iloc[12]}")
    print(f"  Col 15 (script uses as brand): {row.iloc[15]}")
    print(f"  Col 23 (script uses as quantity): {row.iloc[23]}")
    print(f"  Col 27 (script uses as total_price): {row.iloc[27]}")
    print()

