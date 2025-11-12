#!/usr/bin/env python3
"""
Rename "X1" and "x1" to "Altamont Wellness" in budtenders database
Part of Conductor SMS System

Usage: python rename_x1_to_altamont_wellness.py
"""

from supabase import create_client
import json

# Load config
with open('conductor-sms/config.json') as f:
    config = json.load(f)

# Init Supabase
supabase = create_client(
    config['database']['supabase_url'],
    config['database']['supabase_key']
)

print("Checking for 'X1' and 'x1' records...")

# First, check how many records need to be updated
x1_caps = supabase.table('budtenders').select('*', count='exact').eq('dispensary_name', 'X1').execute()
x1_lower = supabase.table('budtenders').select('*', count='exact').eq('dispensary_name', 'x1').execute()

total_count = (x1_caps.count or 0) + (x1_lower.count or 0)

print(f"Found {x1_caps.count or 0} records with 'X1'")
print(f"Found {x1_lower.count or 0} records with 'x1'")
print(f"Total records to update: {total_count}")

if total_count == 0:
    print("No records found to update. Exiting.")
    exit(0)

# Get sample records to show what will be updated
print("\nSample records that will be updated:")
if x1_caps.count and x1_caps.count > 0:
    sample = supabase.table('budtenders').select('id, first_name, last_name, dispensary_name').eq('dispensary_name', 'X1').limit(3).execute()
    for bt in sample.data:
        print(f"  - {bt.get('first_name')} {bt.get('last_name')} (ID: {bt.get('id')})")

if x1_lower.count and x1_lower.count > 0:
    sample = supabase.table('budtenders').select('id, first_name, last_name, dispensary_name').eq('dispensary_name', 'x1').limit(3).execute()
    for bt in sample.data:
        print(f"  - {bt.get('first_name')} {bt.get('last_name')} (ID: {bt.get('id')})")

# Proceed with update
print(f"\nRenaming {total_count} records from 'X1'/'x1' to 'Altamont Wellness'...")

# Update "X1" (capital X)
if x1_caps.count and x1_caps.count > 0:
    print(f"\nUpdating {x1_caps.count} records with 'X1'...")
    result_caps = supabase.table('budtenders').update({'dispensary_name': 'Altamont Wellness'}).eq('dispensary_name', 'X1').execute()
    print(f"Updated {len(result_caps.data)} records")

# Update "x1" (lowercase x)
if x1_lower.count and x1_lower.count > 0:
    print(f"\nUpdating {x1_lower.count} records with 'x1'...")
    result_lower = supabase.table('budtenders').update({'dispensary_name': 'Altamont Wellness'}).eq('dispensary_name', 'x1').execute()
    print(f"Updated {len(result_lower.data)} records")

# Verify the update
print("\nVerifying update...")
remaining_x1_caps = supabase.table('budtenders').select('*', count='exact').eq('dispensary_name', 'X1').execute()
remaining_x1_lower = supabase.table('budtenders').select('*', count='exact').eq('dispensary_name', 'x1').execute()
altamont_count = supabase.table('budtenders').select('*', count='exact').eq('dispensary_name', 'Altamont Wellness').execute()

print(f"Remaining 'X1' records: {remaining_x1_caps.count or 0}")
print(f"Remaining 'x1' records: {remaining_x1_lower.count or 0}")
print(f"Total 'Altamont Wellness' records: {altamont_count.count or 0}")

if (remaining_x1_caps.count or 0) == 0 and (remaining_x1_lower.count or 0) == 0:
    print("\nSUCCESS! All 'X1' and 'x1' records have been renamed to 'Altamont Wellness'")
else:
    print(f"\nWARNING: Some records may still need updating")

