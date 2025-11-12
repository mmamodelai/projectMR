#!/usr/bin/env python3
"""
Check Dispensary Names in Budtenders Table
Part of Conductor SMS System
"""

import os
import sys
from supabase import create_client

# Add parent directory to path for .env
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Supabase connection
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

def main():
    sb = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    print("Fetching all dispensary names from budtenders table...")
    result = sb.table('budtenders').select('dispensary_name').execute()
    
    # Count occurrences
    dispensaries = {}
    for record in result.data:
        name = record.get('dispensary_name')
        if name:
            dispensaries[name] = dispensaries.get(name, 0) + 1
    
    print(f"\nFound {len(dispensaries)} unique dispensary names:\n")
    print("-" * 50)
    for name in sorted(dispensaries.keys()):
        count = dispensaries[name]
        print(f"{name}: {count} budtenders")
    print("-" * 50)
    
    # Check for case-sensitive duplicates
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
            print(f"\nDUPLICATE (case-sensitive): {names}")
            for name in names:
                print(f"  - '{name}': {dispensaries[name]} budtenders")
    
    if not duplicates_found:
        print("No case-sensitive duplicates found!")
    
    # Check for X1/x1 variations
    print("\n" + "=" * 50)
    print("Checking for X1/x1 variations...")
    x1_variations = [name for name in dispensaries.keys() if 'x1' in name.lower()]
    if x1_variations:
        print(f"Found X1 variations: {x1_variations}")
        total = sum(dispensaries[name] for name in x1_variations)
        print(f"Total budtenders: {total}")
    
    # Check for Club W/The W variations
    print("\nChecking for Club W / The W variations...")
    w_variations = [name for name in dispensaries.keys() if 'club w' in name.lower() or 'the w' in name.lower() or name.lower() == 'w']
    if w_variations:
        print(f"Found W variations: {w_variations}")
        total = sum(dispensaries[name] for name in w_variations)
        print(f"Total budtenders: {total}")

if __name__ == "__main__":
    main()

