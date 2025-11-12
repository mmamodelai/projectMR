#!/usr/bin/env python3
"""
Check where the $22,582 lifetime value is stored
"""

from supabase import create_client

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTg0NTA1MSwiZXhwIjoyMDc1NDIxMDUxfQ.o-GId7meaTXwyB4neYjg05oPfRdasvOHs6FHZZyprLs"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=" * 80)
print("WHERE IS THE $22,582 LIFETIME VALUE?")
print("=" * 80)
print()

# Get Luis accounts
luis = supabase.table('customers_blaze').select('*').ilike('name', '%Luis%Bobadilla%').execute()

print("LUIS ACCOUNTS IN CUSTOMERS_BLAZE:")
print("-" * 80)
for acc in luis.data:
    print(f"Name: {acc.get('name')}")
    print(f"   member_id: {acc.get('member_id')}")
    
    # Check for any lifetime value fields
    for key, value in acc.items():
        if 'lifetime' in key.lower() or 'total' in key.lower() or 'value' in key.lower() or 'spend' in key.lower():
            print(f"   {key}: {value}")
    print()

print("=" * 80)

