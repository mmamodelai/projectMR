#!/usr/bin/env python3
"""
Rename "Club W" and "Club w" to "The W" in budtenders database
Part of Conductor SMS System

Usage: python rename_club_w_to_the_w.py
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

print("Checking for 'Club W' and 'Club w' records...")

# First, check how many records need to be updated
club_w_caps = supabase.table('budtenders').select('*', count='exact').eq('dispensary_name', 'Club W').execute()
club_w_lower = supabase.table('budtenders').select('*', count='exact').eq('dispensary_name', 'Club w').execute()

total_count = (club_w_caps.count or 0) + (club_w_lower.count or 0)

print(f"Found {club_w_caps.count or 0} records with 'Club W'")
print(f"Found {club_w_lower.count or 0} records with 'Club w'")
print(f"Total records to update: {total_count}")

if total_count == 0:
    print("No records found to update. Exiting.")
    exit(0)

# Get sample records to show what will be updated
print("\nSample records that will be updated:")
if club_w_caps.count and club_w_caps.count > 0:
    sample = supabase.table('budtenders').select('id, first_name, last_name, dispensary_name').eq('dispensary_name', 'Club W').limit(3).execute()
    for bt in sample.data:
        print(f"  - {bt.get('first_name')} {bt.get('last_name')} (ID: {bt.get('id')})")

if club_w_lower.count and club_w_lower.count > 0:
    sample = supabase.table('budtenders').select('id, first_name, last_name, dispensary_name').eq('dispensary_name', 'Club w').limit(3).execute()
    for bt in sample.data:
        print(f"  - {bt.get('first_name')} {bt.get('last_name')} (ID: {bt.get('id')})")

# Proceed with update
print(f"\nRenaming {total_count} records from 'Club W'/'Club w' to 'The W'...")

# Update "Club W" (capital W)
if club_w_caps.count and club_w_caps.count > 0:
    print(f"\nUpdating {club_w_caps.count} records with 'Club W'...")
    result_caps = supabase.table('budtenders').update({'dispensary_name': 'The W'}).eq('dispensary_name', 'Club W').execute()
    print(f"Updated {len(result_caps.data)} records")

# Update "Club w" (lowercase w)
if club_w_lower.count and club_w_lower.count > 0:
    print(f"\nUpdating {club_w_lower.count} records with 'Club w'...")
    result_lower = supabase.table('budtenders').update({'dispensary_name': 'The W'}).eq('dispensary_name', 'Club w').execute()
    print(f"Updated {len(result_lower.data)} records")

# Verify the update
print("\nVerifying update...")
remaining_club_w = supabase.table('budtenders').select('*', count='exact').eq('dispensary_name', 'Club W').execute()
remaining_club_w_lower = supabase.table('budtenders').select('*', count='exact').eq('dispensary_name', 'Club w').execute()
the_w_count = supabase.table('budtenders').select('*', count='exact').eq('dispensary_name', 'The W').execute()

print(f"Remaining 'Club W' records: {remaining_club_w.count or 0}")
print(f"Remaining 'Club w' records: {remaining_club_w_lower.count or 0}")
print(f"Total 'The W' records: {the_w_count.count or 0}")

if (remaining_club_w.count or 0) == 0 and (remaining_club_w_lower.count or 0) == 0:
    print("\nSUCCESS! All 'Club W' and 'Club w' records have been renamed to 'The W'")
else:
    print(f"\nWARNING: Some records may still need updating")

