#!/usr/bin/env python3
"""
Fix Dispensary Names - Direct Update
Part of Conductor SMS System
"""

import os
import sys
from supabase import create_client

# Supabase connection
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

# Mapping of wrong names to correct names
FIXES = {
    'x1': 'Altamont Wellness',
    'X1': 'Altamont Wellness',
    'Club W': 'The W',
    'Club w': 'The W',
    'phenos': 'Phenos',
    'firehouse': 'Firehouse',
    'Higher level': 'Higher Level',
}

def main():
    sb = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    print("=" * 60)
    print("FIXING DISPENSARY NAMES")
    print("=" * 60)
    
    total_fixed = 0
    
    for wrong_name, correct_name in FIXES.items():
        print(f"\nFixing '{wrong_name}' -> '{correct_name}'...")
        
        # Get affected budtenders
        result = sb.table('budtenders').select('id, first_name, last_name, dispensary_name').eq('dispensary_name', wrong_name).execute()
        
        if not result.data:
            print(f"  No records found with '{wrong_name}'")
            continue
        
        count = len(result.data)
        print(f"  Found {count} budtenders to update:")
        
        for budtender in result.data:
            name = f"{budtender.get('first_name', '')} {budtender.get('last_name', '')}".strip()
            if not name:
                name = f"ID {budtender['id']}"
            print(f"    - {name}")
        
        # Update all at once
        update_result = sb.table('budtenders').update({
            'dispensary_name': correct_name
        }).eq('dispensary_name', wrong_name).execute()
        
        print(f"  Updated {count} records")
        total_fixed += count
    
    print("\n" + "=" * 60)
    print(f"TOTAL FIXED: {total_fixed} budtender records")
    print("=" * 60)
    
    # Show final state
    print("\nFinal dispensary list:")
    result = sb.table('budtenders').select('dispensary_name').execute()
    
    dispensaries = {}
    for record in result.data:
        name = record.get('dispensary_name')
        if name:
            dispensaries[name] = dispensaries.get(name, 0) + 1
    
    print("\n" + "-" * 60)
    for name in sorted(dispensaries.keys()):
        count = dispensaries[name]
        print(f"{name}: {count} budtenders")
    print("-" * 60)
    
    # Check for remaining case-sensitive duplicates
    print("\nChecking for case-sensitive duplicates...")
    lower_map = {}
    for name in dispensaries.keys():
        lower = name.lower()
        if lower not in lower_map:
            lower_map[lower] = []
        lower_map[lower].append(name)
    
    duplicates_found = False
    for lower, names in lower_map.items():
        if len(names) > 1:
            duplicates_found = True
            print(f"  WARNING: {names}")
    
    if not duplicates_found:
        print("  No case-sensitive duplicates found!")
        print("\n  SUCCESS! All dispensary names are clean.")
    else:
        print("\n  WARNING: Some duplicates still exist.")
    
    print("\n" + "=" * 60)
    print("DONE!")
    print("=" * 60)

if __name__ == "__main__":
    main()



