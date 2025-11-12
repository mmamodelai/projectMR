#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check Transaction 569043 in detail
"""
import sys
import os
import pandas as pd
from supabase import create_client

# Set UTF-8 encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Supabase connection
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=" * 100)
print("Transaction 569043 - DETAILED ANALYSIS")
print("=" * 100)

# Get from database
print("\n[DATABASE]")
trans = supabase.table('transactions').select('*').eq('transaction_id', 569043).execute()
if trans.data:
    t = trans.data[0]
    print(f"Transaction Total: ${t.get('total_amount', 0):.2f}")
    print(f"Date: {t.get('date')}")

items = supabase.table('transaction_items').select('*').eq('transaction_id', 569043).execute()
print(f"\nItems in DB: {len(items.data)}")
for item in items.data:
    qty = int(item.get('quantity', 0))
    unit_price = float(item.get('unit_price', 0))
    total = float(item.get('total_price', 0))
    calculated = qty * unit_price
    print(f"  {item.get('product_name')}")
    print(f"    Qty: {qty}, Unit Price: ${unit_price:.2f}, Total: ${total:.2f} (calc: ${calculated:.2f})")

# Get from CSV
print("\n[CSV SOURCE]")
for encoding in ['latin-1', 'utf-8', 'cp1252']:
    try:
        df = pd.read_csv('total_sales_products.csv', encoding=encoding)
        print(f"Loaded CSV with {encoding}")
        break
    except:
        continue

t569043 = df[df['Trans No'] == 569043]
print(f"\nItems in CSV: {len(t569043)}")
for idx, row in t569043.iterrows():
    print(f"  {row['Product']}")
    print(f"    Qty: {row['Quantity Sold']}, Retail Price: ${row['Retail Price']:.2f}, Total Due: ${row['Total Due']:.2f}")

print("\n" + "=" * 100)
print("PROBLEM IDENTIFIED:")
print("If items in DB show unit_price = item's total (not per-unit price), then we imported the wrong column!")
print("=" * 100)

