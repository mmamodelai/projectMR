#!/usr/bin/env python3
"""
Quick script to check September 2025 statistics from the CSV
"""

import pandas as pd

# Load the CSV
df = pd.read_csv('total_sales_products.csv', skiprows=1, encoding='latin-1')

# Parse dates from first column
df['date'] = pd.to_datetime(df.iloc[:, 0])

# Filter for September 2025
sept_data = df[df['date'].dt.strftime('%Y-%m') == '2025-09']

# Get statistics
unique_customers = sept_data.iloc[:, 4].nunique()  # Customer ID is in column 4
total_transactions = len(sept_data)

print("September 2025 Statistics:")
print(f"Total transactions: {total_transactions:,}")
print(f"Unique customers: {unique_customers:,}")

if len(sept_data) > 0:
    print(f"Date range: {sept_data['date'].min()} to {sept_data['date'].max()}")
    
    # Show some sample data
    print("\nSample transactions:")
    sample = sept_data.iloc[:5, [0, 4, 19]]  # Date, Trans No, Customer ID
    print(sample.to_string())
else:
    print("No September 2025 data found")

# Also check what months we do have
print(f"\nAvailable months in data:")
month_counts = df.groupby(df['date'].dt.strftime('%Y-%m')).size().sort_index()
print(month_counts.tail(10))
