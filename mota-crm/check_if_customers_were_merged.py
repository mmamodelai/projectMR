#!/usr/bin/env python3
"""
Check if customers_blaze was manually cleaned/merged
"""

from supabase import create_client

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTg0NTA1MSwiZXhwIjoyMDc1NDIxMDUxfQ.o-GId7meaTXwyB4neYjg05oPfRdasvOHs6FHZZyprLs"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=" * 80)
print("DID WE MANUALLY MERGE CUSTOMERS?")
print("=" * 80)
print()

# Check if there are archive tables with old customer data
print("1. CHECKING FOR BACKUP TABLES")
print("-" * 80)

# Try common backup table names
backup_tables = [
    'customers_blaze_backup_20251106',
    'customers_blaze_old_backup',
    'transaction_items_old_20251107',
    'customers_backup',
    'customers_old'
]

for table in backup_tables:
    try:
        result = supabase.table(table).select('id', count='exact').limit(1).execute()
        print(f"   {table}: {result.count:,} rows FOUND")
    except:
        print(f"   {table}: NOT FOUND")

print()
print("=" * 80)

