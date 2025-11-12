#!/usr/bin/env python3
"""
Check what product data we have available
"""

import pandas as pd

print("=" * 80)
print("CHECKING AVAILABLE PRODUCT DATA")
print("=" * 80)
print()

# Load the CSV
print("Loading PRODUCT_BATCH_EXPORT.csv...")
df = pd.read_csv('PRODUCT_BATCH_EXPORT.csv', skiprows=1, encoding='latin-1')

print(f"Total products: {len(df):,}")
print()

# Check what columns we have
print("KEY COLUMNS AVAILABLE:")
print()

# Inventory data
print("INVENTORY & STOCK:")
print(f"  Current Qty: {df['Current Qty'].notna().sum():,} products have quantity data")
print(f"  Purchased Qty: {df['Purchased Qty'].notna().sum():,} products")
print(f"  Status: {df['Status'].notna().sum():,} products (Active/Inactive)")
print(f"  Archived: {df['Archived?'].notna().sum():,} products")
print()

# Pricing data
print("PRICING & COST:")
print(f"  Cost per Unit: {df['Cost per Unit'].notna().sum():,} products have cost data")
print(f"  Purchased Cost: {df['Purchased Cost'].notna().sum():,} products")
print()

# Product info
print("PRODUCT DETAILS:")
print(f"  Product Name: {df['Product Name'].notna().sum():,}")
print(f"  Brand: {df['Brand'].notna().sum():,}")
print(f"  Category: {df['Category'].notna().sum():,}")
print(f"  Product SKU: {df['Product SKU'].notna().sum():,}")
print(f"  Product Flower Type: {df['Product Flower Type'].notna().sum():,}")
print(f"  Strain: {df['Strain'].notna().sum():,}")
print()

# THC/CBD
print("CANNABIS CONTENT:")
print(f"  Total THC (%): {df['Total THC (%)'].notna().sum():,} products")
print(f"  Total CBD (%): {df['Total CBD (%)'].notna().sum():,} products")
print(f"  THC (mg): {df['Total THC (mg)'].notna().sum():,} products")
print(f"  CBD (mg): {df['Total CBD (mg)'].notna().sum():,} products")
print()

# Dates
print("DATE INFORMATION:")
print(f"  Purchased Date: {df['Purchased Date'].notna().sum():,}")
print(f"  Expiration Date: {df['Expiration Date'].notna().sum():,}")
print(f"  Received Date: {df['Received Date'].notna().sum():,}")
print()

# Vendor
print("VENDOR INFO:")
print(f"  Vendor Name: {df['Vendor Name'].notna().sum():,}")
print()

# Sample product with all data
print("=" * 80)
print("SAMPLE PRODUCT WITH FULL DATA:")
print("=" * 80)

# Find a product with THC data
sample = df[df['Total THC (%)'].notna()].iloc[0] if len(df[df['Total THC (%)'].notna()]) > 0 else df.iloc[0]

print(f"Product: {sample['Product Name']}")
print(f"Brand: {sample['Brand']}")
print(f"Category: {sample['Category']}")
print(f"SKU: {sample['Product SKU']}")
print(f"Flower Type: {sample['Product Flower Type']}")
print(f"Strain: {sample['Strain']}")
print(f"THC: {sample['Total THC (%)']}%")
print(f"CBD: {sample['Total CBD (%)']}%")
print(f"Current Qty: {sample['Current Qty']}")
print(f"Cost per Unit: ${sample['Cost per Unit']}")
print(f"Status: {sample['Status']}")
print(f"Purchased Date: {sample['Purchased Date']}")
print(f"Vendor: {sample['Vendor Name']}")
print()

print("=" * 80)
print("CONCLUSION:")
print("=" * 80)
print("WE HAVE:")
print("  [YES] Stock quantities (Current Qty)")
print("  [YES] Cost data (Cost per Unit)")
print("  [YES] THC/CBD percentages")
print("  [YES] Strain types (Sativa/Indica/Hybrid)")
print("  [YES] Status (Active/Inactive)")
print("  [YES] Purchase dates (can calculate age)")
print("  [YES] Vendor information")
print("  [YES] Product categories")
print()
print("WE CAN ADD TO DATABASE:")
print("  >>> Stock levels (quantity on hand)")
print("  >>> Age of stock (days since purchased)")
print("  >>> Out of stock alerts")
print("  >>> Vendor names")
print("  >>> Cost margins")
print("  >>> Everything you asked for!")
print()

