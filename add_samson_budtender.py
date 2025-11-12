#!/usr/bin/env python3
"""
Add Samson T to XB (External Budtenders) Database
Part of Conductor SMS System
"""

from supabase import create_client, Client

# Supabase connection
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTg0NTA1MSwiZXhwIjoyMDc1NDIxMDUxfQ.o-GId7meaTXwyB4neYjg05oPfRdasvOHs6FHZZyprLs"

print("=" * 60)
print("ADD TEST BUDTENDER - Samson T")
print("=" * 60)
print()

# Initialize Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Budtender details
budtender_data = {
    'first_name': 'Samson',
    'last_name': 'T',
    'phone': '+16198004766',  # Formatted to E.164
    'email': 'mota.la.rewards+samson@gmail.com',
    'dispensary_name': 'Higher Level',  # XB location
    'points': 0  # Starting points
}

print("Adding budtender with details:")
print(f"  Name:        {budtender_data['first_name']} {budtender_data['last_name']}")
print(f"  Phone:       {budtender_data['phone']}")
print(f"  Email:       {budtender_data['email']}")
print(f"  Location:    {budtender_data['dispensary_name']}")
print(f"  Points:      {budtender_data['points']}")
print()

try:
    # Check if already exists
    existing = supabase.table('budtenders') \
        .select('*') \
        .eq('phone', '+16198004766') \
        .execute()
    
    if existing.data:
        print("WARNING: Budtender already exists:")
        for b in existing.data:
            print(f"  ID: {b.get('id')}")
            print(f"  Name: {b.get('first_name')} {b.get('last_name')}")
            print(f"  Location: {b.get('dispensary_name')}")
            print(f"  Points: {b.get('points')}")
        print()
        
        update = input("Update existing record? (yes/no): ")
        if update.lower() == 'yes':
            result = supabase.table('budtenders') \
                .update(budtender_data) \
                .eq('phone', '+16198004766') \
                .execute()
            print("SUCCESS: Budtender updated!")
        else:
            print("Cancelled.")
    else:
        # Insert new budtender
        result = supabase.table('budtenders').insert(budtender_data).execute()
        print("SUCCESS: Budtender added successfully!")
        print()
        
        # Show the created record
        if result.data:
            new_budtender = result.data[0]
            print("Created record:")
            print(f"  ID:          {new_budtender.get('id')}")
            print(f"  Name:        {new_budtender.get('first_name')} {new_budtender.get('last_name')}")
            print(f"  Phone:       {new_budtender.get('phone')}")
            print(f"  Email:       {new_budtender.get('email')}")
            print(f"  Location:    {new_budtender.get('dispensary_name')}")
            print(f"  Points:      {new_budtender.get('points')}")
    
    print()
    print("=" * 60)
    print("COMPLETE!")
    print("=" * 60)
    
except Exception as e:
    print(f"ERROR: {e}")
    print()
    print("Troubleshooting:")
    print("  - Check if 'budtenders' table exists in Supabase")
    print("  - Verify service role key has write permissions")
    print("  - Check table structure matches expected fields")

