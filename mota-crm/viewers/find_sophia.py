#!/usr/bin/env python3
"""
Find Sophia in Budtenders Table
"""

from supabase import create_client

# Supabase connection
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

def main():
    sb = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    print("=" * 60)
    print("SEARCHING FOR SOPHIA")
    print("=" * 60)
    
    # Search by first name containing "sophia" (case-insensitive)
    print("\nSearching for any budtender with 'Sophia' in first name...")
    result = sb.table('budtenders').select('*').ilike('first_name', '%sophia%').execute()
    
    if result.data:
        print(f"Found {len(result.data)} record(s):")
        for b in result.data:
            print(f"\n  ID: {b.get('id')}")
            print(f"  Name: {b.get('first_name')} {b.get('last_name')}")
            print(f"  Dispensary: {b.get('dispensary_name')}")
            print(f"  Phone: {b.get('phone')}")
            print(f"  Email: {b.get('email')}")
            print(f"  Points: {b.get('points', 0)}")
            print(f"  Created: {b.get('created_at')}")
            print(f"  Updated: {b.get('updated_at')}")
    else:
        print("  No records found with first name containing 'Sophia'")
    
    # Also search last name
    print("\n" + "-" * 60)
    print("Searching for any budtender with 'Sophia' in last name...")
    result = sb.table('budtenders').select('*').ilike('last_name', '%sophia%').execute()
    
    if result.data:
        print(f"Found {len(result.data)} record(s):")
        for b in result.data:
            print(f"\n  ID: {b.get('id')}")
            print(f"  Name: {b.get('first_name')} {b.get('last_name')}")
            print(f"  Dispensary: {b.get('dispensary_name')}")
    else:
        print("  No records found with last name containing 'Sophia'")
    
    # Search Firehouse budtenders
    print("\n" + "-" * 60)
    print("All Firehouse budtenders:")
    result = sb.table('budtenders').select('id, first_name, last_name, phone, points').eq('dispensary_name', 'Firehouse').order('last_name').execute()
    
    if result.data:
        print(f"\nFound {len(result.data)} Firehouse budtenders:")
        for b in result.data:
            name = f"{b.get('first_name', '')} {b.get('last_name', '')}".strip()
            print(f"  - {name} (ID: {b.get('id')}, Points: {b.get('points', 0)})")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()



