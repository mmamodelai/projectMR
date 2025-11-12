#!/usr/bin/env python3
"""Quick fetch of sales totals"""

from supabase import create_client
from datetime import datetime

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

periods = [
    ("September 2025", "2025-09-01", "2025-09-30"),
    ("October 2025", "2025-10-01", "2025-10-31"),
    ("November 1-5, 2025", "2025-11-01", "2025-11-05"),
    ("December 2024", "2024-12-01", "2024-12-31"),
]

print("\n" + "="*80)
print("SALES DATA - BLAZE API DATABASE")
print("="*80 + "\n")

for period_name, start_date, end_date in periods:
    # Fetch transactions
    response = supabase.table('transactions_blaze') \
        .select('total_amount') \
        .gte('date', f'{start_date}T00:00:00') \
        .lte('date', f'{end_date}T23:59:59') \
        .eq('blaze_status', 'Completed') \
        .gt('total_amount', 0) \
        .execute()
    
    if response.data:
        count = len(response.data)
        total = sum(t['total_amount'] for t in response.data)
        
        print(f"{period_name}:")
        print(f"  Transactions: {count:,}")
        print(f"  Total Revenue: ${total:,.2f}")
        print()
    else:
        print(f"{period_name}:")
        print(f"  NO DATA FOUND")
        print()

print("="*80)



