#!/usr/bin/env python3
from supabase import create_client

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

sb = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=" * 80)
print("INVESTIGATING TIMEZONE/DOB ISSUE")
print("=" * 80)

# Get Stephen Clare records with RAW data
stephens = sb.table('customers_blaze')\
    .select('member_id, first_name, last_name, date_of_birth, created_at')\
    .ilike('first_name', 'stephen')\
    .ilike('last_name', 'clare')\
    .execute()

print(f"\nFound {len(stephens.data)} Stephen Clare records:\n")

for s in stephens.data:
    print(f"Record: {s['first_name']} {s['last_name']}")
    print(f"  ID: {s['member_id']}")
    print(f"  DOB (raw from DB): {s.get('date_of_birth')}")
    print(f"  DOB (type): {type(s.get('date_of_birth'))}")
    print(f"  Created at: {s.get('created_at')}")
    print()

# Check what the database actually stores
print("=" * 80)
print("CHECKING DATABASE STORAGE FORMAT")
print("=" * 80)

# Sample a few customers with DOB
sample = sb.table('customers_blaze')\
    .select('first_name, last_name, date_of_birth')\
    .not_.is_('date_of_birth', 'null')\
    .limit(10)\
    .execute()

print("\nSample of 10 DOBs from database:")
for c in sample.data:
    dob = c.get('date_of_birth')
    print(f"  {c['first_name']} {c['last_name']}: '{dob}' (type: {type(dob)})")

# Check if there are MANY people with 1-day DOB differences
print("\n" + "=" * 80)
print("HOW MANY PEOPLE HAVE 1-DAY DOB DIFFERENCES?")
print("=" * 80)

# This query will be slow, but let's try
print("\nSearching for potential ±1 day duplicates...")
print("(This might take a moment...)")

# Just check a sample
sample_for_dupes = sb.table('customers_blaze')\
    .select('first_name, last_name, date_of_birth')\
    .not_.is_('date_of_birth', 'null')\
    .limit(1000)\
    .execute()

# Group by name
from collections import defaultdict
name_groups = defaultdict(list)
for c in sample_for_dupes.data:
    key = (c['first_name'].lower().strip(), c['last_name'].lower().strip())
    name_groups[key].append(c['date_of_birth'])

# Find groups with ±1 day differences
suspicious = []
for name, dobs in name_groups.items():
    if len(set(dobs)) > 1:  # Multiple different DOBs
        # Check if any are ±1 day apart
        for i, dob1 in enumerate(dobs):
            for dob2 in dobs[i+1:]:
                if dob1 and dob2:
                    # Parse dates
                    from datetime import datetime
                    try:
                        d1 = datetime.fromisoformat(dob1.replace('Z', '+00:00')).date()
                        d2 = datetime.fromisoformat(dob2.replace('Z', '+00:00')).date()
                        diff = abs((d1 - d2).days)
                        if diff == 1:
                            suspicious.append((name, dob1, dob2, diff))
                    except:
                        pass

print(f"\nFound {len(suspicious)} people with ±1 day DOB differences in sample:")
for name, dob1, dob2, diff in suspicious[:10]:
    print(f"  {name[0]} {name[1]}: {dob1} vs {dob2} ({diff} day)")

if len(suspicious) > 10:
    print(f"  ... and {len(suspicious) - 10} more")

print("\n" + "=" * 80)
print("THEORY:")
print("=" * 80)
print("If DOBs are stored as DATE (not DATETIME), timezone shouldn't matter.")
print("But if they're stored as '1983-02-05 00:00:00 UTC' and displayed in")
print("Pacific time, you'd see '1983-02-04 16:00:00 PST' = Feb 4th!")
print("\nThis is EXACTLY what's happening!")

