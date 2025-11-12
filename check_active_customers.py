#!/usr/bin/env python3
"""
Check how many active customers we have with contact info
"""
from supabase import create_client
from datetime import datetime, timedelta

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

sb = create_client(SUPABASE_URL, SUPABASE_KEY)

print("Checking customer database stats...")
print("=" * 60)

# Total customers
total = sb.table('customers_blaze').select('id', count='exact').execute()
print(f"Total customers: {total.count:,}")

# Customers with email
with_email = sb.table('customers_blaze').select('id', count='exact').neq('email', None).neq('email', '').execute()
print(f"With email: {with_email.count:,}")

# Customers with phone
with_phone = sb.table('customers_blaze').select('id', count='exact').neq('phone', None).neq('phone', '').execute()
print(f"With phone: {with_phone.count:,}")

# Customers with BOTH email AND phone
with_both = sb.table('customers_blaze').select('id', count='exact').neq('email', None).neq('email', '').neq('phone', None).neq('phone', '').execute()
print(f"With BOTH email AND phone: {with_both.count:,}")

# Last visited within 180 days (6 months)
six_months_ago = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
print(f"\nChecking last visited since: {six_months_ago}")

recent_visitors = sb.table('customers_blaze').select('id', count='exact').gte('last_visited', six_months_ago).execute()
print(f"Visited within last 180 days: {recent_visitors.count:,}")

# THE GOLDEN QUERY: Has email AND phone AND visited within 180 days
golden = sb.table('customers_blaze').select('id', count='exact')\
    .neq('email', None).neq('email', '')\
    .neq('phone', None).neq('phone', '')\
    .gte('last_visited', six_months_ago)\
    .execute()

print("=" * 60)
print(f"ACTIVE CUSTOMERS (Email + Phone + Visited <180 days): {golden.count:,}")
print("=" * 60)

# Additional breakdowns
print("\nAdditional insights:")

# 90 days
ninety_days = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
golden_90 = sb.table('customers_blaze').select('id', count='exact')\
    .neq('email', None).neq('email', '')\
    .neq('phone', None).neq('phone', '')\
    .gte('last_visited', ninety_days)\
    .execute()
print(f"Active <90 days (Email + Phone): {golden_90.count:,}")

# 30 days
thirty_days = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
golden_30 = sb.table('customers_blaze').select('id', count='exact')\
    .neq('email', None).neq('email', '')\
    .neq('phone', None).neq('phone', '')\
    .gte('last_visited', thirty_days)\
    .execute()
print(f"Active <30 days (Email + Phone): {golden_30.count:,}")

# 365 days
one_year = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
golden_365 = sb.table('customers_blaze').select('id', count='exact')\
    .neq('email', None).neq('email', '')\
    .neq('phone', None).neq('phone', '')\
    .gte('last_visited', one_year)\
    .execute()
print(f"Active <365 days (Email + Phone): {golden_365.count:,}")

