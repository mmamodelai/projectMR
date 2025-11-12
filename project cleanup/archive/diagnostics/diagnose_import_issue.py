#!/usr/bin/env python3
"""
Diagnose why only 4 of 8 items were imported for transaction 550995
"""

import pandas as pd
from supabase import create_client

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

sb = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=" * 80)
print("DIAGNOSIS: Why are 4 items missing from transaction 550995?")
print("=" * 80)

# Load CSV
df = pd.read_csv('total_sales_products.csv', skiprows=1, encoding='latin-1')
trans_csv = df[df.iloc[:, 4].astype(str) == '550995']

print(f"\nCSV has {len(trans_csv)} items for transaction 550995")
print("Row indices in CSV:", trans_csv.index.tolist())

# Check what's in DB
items_db = sb.table('transaction_items').select('*').eq('transaction_id', '550995').execute()

print(f"\nDatabase has {len(items_db.data)} items for transaction 550995")

# Check row numbers
print("\n" + "=" * 80)
print("ROW NUMBER ANALYSIS:")
print("=" * 80)
print(f"First 4 items are at rows: {trans_csv.index.tolist()[:4]}")
print(f"Last 4 items are at rows:  {trans_csv.index.tolist()[4:]}")
print()
print("The first 4 items (rows 61102-61179) were imported")
print("The last 4 items (rows 65464-65486) were NOT imported")
print()

# Check if there's a pattern
print("=" * 80)
print("HYPOTHESIS: Was there a row limit during import?")
print("=" * 80)

# Get total transaction_items count
count = sb.table('transaction_items').select('id', count='exact').execute()
print(f"\nTotal items in database: {count.count:,}")
print(f"Total rows in CSV: {len(df):,}")
print(f"Missing rows: {len(df) - count.count:,}")

# Check if import stopped at a certain row
# Find highest row index that was imported
print("\nChecking if import stopped at a specific row...")

# Sample some SKUs from later rows
late_row_skus = [
    df.iloc[65464, 11],  # Row 65464
    df.iloc[65471, 11],  # Row 65471  
    df.iloc[65477, 11],  # Row 65477
    df.iloc[65486, 11]   # Row 65486
]

print(f"\nChecking if these late-row SKUs exist in database:")
for i, sku in enumerate(late_row_skus):
    result = sb.table('transaction_items').select('id').eq('product_sku', str(sku)).limit(1).execute()
    status = "FOUND" if result.data else "MISSING"
    print(f"  Row {[65464, 65471, 65477, 65486][i]} SKU: {status}")

print("\n" + "=" * 80)
print("CONCLUSION:")
print("=" * 80)
print("If all late-row SKUs are MISSING, the import likely stopped early")
print("or processed only the first ~60,000-65,000 rows of the CSV.")
print()
print("SOLUTION: Re-run the import script to process ALL rows.")

