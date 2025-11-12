#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check Transaction 549912 - Missing Items Investigation
"""
import sys
import os
from supabase import create_client

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Supabase connection
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=" * 80)
print("TRANSACTION 549912 INVESTIGATION")
print("=" * 80)

# Get transaction details
trans = supabase.table('transactions').select('*').eq('id', 549912).execute()
if trans.data:
    t = trans.data[0]
    print(f"\nTRANSACTION INFO:")
    print(f"   ID: {t['id']}")
    print(f"   Date: {t.get('transaction_date', 'N/A')}")
    print(f"   Total: ${t.get('total_amount', 0):.2f}")
    print(f"   Customer: {t.get('customer_name', 'N/A')}")

# Get items from database
items = supabase.table('transaction_items').select('*').eq('transaction_id', 549912).execute()
print(f"\nITEMS IN DATABASE: {len(items.data)}")
db_total = 0
for item in items.data:
    subtotal = float(item['unit_price']) * int(item['quantity'])
    db_total += subtotal
    print(f"   {item['product_name']}: ${item['unit_price']} x {item['quantity']} = ${subtotal:.2f}")

print(f"\nDATABASE ITEM TOTAL: ${db_total:.2f}")
if trans.data:
    expected = float(trans.data[0].get('total_amount', 0))
    print(f"TRANSACTION TOTAL: ${expected:.2f}")
    print(f"MISSING: ${expected - db_total:.2f}")

# Check CSV
print(f"\nCHECKING CSV FILE...")
import pandas as pd
try:
    # Try different encodings
    for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
        try:
            df = pd.read_csv('total_sales_products.csv', encoding=encoding)
            print(f"   Loaded CSV with {encoding} encoding")
            break
        except UnicodeDecodeError:
            continue
    
    t549912 = df[df['Trans No'] == 549912]
    print(f"\nITEMS IN CSV: {len(t549912)}")
    csv_total = 0
    for idx, row in t549912.iterrows():
        try:
            qty = int(row['Quantity Sold']) if pd.notna(row['Quantity Sold']) else 0
            price = float(row['Retail Price']) if pd.notna(row['Retail Price']) else 0.0
            subtotal = qty * price
            csv_total += subtotal
            print(f"   {row['Product']}: ${price:.2f} x {qty} = ${subtotal:.2f}")
        except Exception as e:
            print(f"   ERROR parsing row: {e}")
    
    print(f"\nCSV ITEM TOTAL: ${csv_total:.2f}")
    
    # Find missing items
    csv_products = set(t549912['Product'].tolist())
    db_products = set(item['product_name'] for item in items.data)
    missing = csv_products - db_products
    
    if missing:
        print(f"\nMISSING ITEMS (in CSV but not in DB):")
        for product in missing:
            row = t549912[t549912['Product'] == product].iloc[0]
            print(f"   - {product}: ${row['Retail Price']} x {row['Quantity Sold']}")

except Exception as e:
    print(f"   ERROR reading CSV: {e}")

print("\n" + "=" * 80)

