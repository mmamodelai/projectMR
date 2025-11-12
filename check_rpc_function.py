#!/usr/bin/env python3
"""
Check if RPC function exists and what it returns
"""

from supabase import create_client, Client

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("Checking if get_customers_fast RPC exists...")

try:
    result = supabase.rpc('get_customers_fast', {
        'filter_email': False,
        'filter_phone': False,
        'days_cutoff': 365
    }).limit(5).execute()
    
    print(f"RPC function exists!")
    print(f"  Returned {len(result.data)} customers")
    
    if result.data:
        print("\nFirst 3 customers:")
        for i, c in enumerate(result.data[:3], 1):
            name = c.get('name') or f"{c.get('first_name', '')} {c.get('last_name', '')}".strip()
            last_visit = c.get('last_visited', 'N/A')
            print(f"  {i}. {name} - Last visit: {last_visit}")
        
        print("\nHow are they ordered?")
        dates = [c.get('last_visited') for c in result.data if c.get('last_visited')]
        if dates:
            print(f"  First customer last visit: {dates[0]}")
            print(f"  Last customer last visit: {dates[-1]}")
            
            # Check if descending (newest first)
            if dates == sorted(dates, reverse=True):
                print("  Ordered by last_visited DESC (newest first) - CORRECT!")
            elif dates == sorted(dates):
                print("  Ordered by last_visited ASC (oldest first) - WRONG! NEED TO FIX!")
            else:
                print("  Not ordered by last_visited - NEED TO ADD ORDER BY!")
    
except Exception as e:
    print(f"RPC function not available: {e}")
    print("\nThe viewer is probably not using RPC function.")
    print("We need to add ORDER BY to the direct query instead.")

print("\nDone!")

