#!/usr/bin/env python3
"""
Delete Catalyst Pomona Budtender(s)
"""

from supabase import create_client

# Supabase connection
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

def main():
    sb = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    print("=" * 60)
    print("DELETING CATALYST POMONA BUDTENDER(S)")
    print("=" * 60)
    
    # Find Catalyst budtenders
    print("\nFinding Catalyst Pomona budtenders...")
    result = sb.table('budtenders').select('*').eq('dispensary_name', 'Catalyst Pomona').execute()
    
    if not result.data:
        print("  No budtenders found at Catalyst Pomona")
        return
    
    print(f"\nFound {len(result.data)} budtender(s):")
    for b in result.data:
        name = f"{b.get('first_name', '')} {b.get('last_name', '')}".strip()
        print(f"\n  ID: {b.get('id')}")
        print(f"  Name: {name}")
        print(f"  Phone: {b.get('phone')}")
        print(f"  Email: {b.get('email')}")
        print(f"  Points: {b.get('points', 0)}")
    
    # Delete them
    print("\n" + "-" * 60)
    print("Deleting budtender(s)...")
    
    delete_result = sb.table('budtenders').delete().eq('dispensary_name', 'Catalyst Pomona').execute()
    
    print(f"Deleted {len(result.data)} budtender record(s)")
    
    # Verify deletion
    print("\n" + "-" * 60)
    print("Verifying deletion...")
    verify = sb.table('budtenders').select('id').eq('dispensary_name', 'Catalyst Pomona').execute()
    
    if not verify.data:
        print("  SUCCESS! No Catalyst Pomona budtenders remaining.")
    else:
        print(f"  WARNING: Still found {len(verify.data)} record(s)")
    
    print("\n" + "=" * 60)
    print("DONE!")
    print("=" * 60)

if __name__ == "__main__":
    main()



