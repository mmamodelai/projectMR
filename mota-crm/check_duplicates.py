#!/usr/bin/env python3
"""
Quick Duplicate Checker
Shows current duplicate status
"""

from supabase import create_client, Client

# Initialize Supabase
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

sb: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=" * 60)
print("Checking Duplicate Status...")
print("=" * 60)

# Get all customers
result = sb.table('customers_blaze')\
    .select('member_id, first_name, last_name, date_of_birth')\
    .not_.is_('first_name', 'null')\
    .not_.is_('last_name', 'null')\
    .execute()

total_records = len(result.data)

# Group by first_name + last_name + DOB
groups = {}
for customer in result.data:
    key = (
        customer['first_name'].lower().strip(),
        customer['last_name'].lower().strip(),
        customer.get('date_of_birth', 'null')
    )
    
    if key not in groups:
        groups[key] = []
    groups[key].append(customer)

# Count duplicates
unique_people = len(groups)
duplicate_groups = [g for g in groups.values() if len(g) > 1]
total_duplicates = sum(len(g) - 1 for g in duplicate_groups)

print(f"\nRESULTS:")
print(f"   Total customer records: {total_records:,}")
print(f"   Unique people: {unique_people:,}")
print(f"   Duplicate records: {total_duplicates:,}")
print(f"   Duplicate groups: {len(duplicate_groups):,}")

if total_duplicates == 0:
    print("\n>>> NO DUPLICATES! Database is clean!")
else:
    print(f"\n>>> Still {total_duplicates:,} duplicates to merge")
    print(f"    Run merge_duplicates.bat again to continue")
    
    # Show top 10 duplicate groups
    print(f"\nTop 10 Duplicate Groups:")
    duplicate_groups_sorted = sorted(duplicate_groups, key=len, reverse=True)
    for i, group in enumerate(duplicate_groups_sorted[:10], 1):
        customer = group[0]
        name = f"{customer['first_name']} {customer['last_name']}"
        print(f"   {i}. {name}: {len(group)} records")

print("\n" + "=" * 60)
input("\nPress Enter to close...")

