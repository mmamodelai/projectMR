#!/usr/bin/env python3
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

# Search for budtender by ID
response = supabase.table('budtenders').select('*').eq('id', 2098531854).execute()

if response.data:
    budtender = response.data[0]
    print(f"Found Budtender: {budtender.get('first_name')} {budtender.get('last_name')}")
    print(f"  ID: {budtender.get('id')}")
    print(f"  Points: {budtender.get('points', 0)}")
    print(f"  Dispensary: {budtender.get('dispensary_name')}")
    print(f"  Email: {budtender.get('email')}")
    print(f"  Phone: {budtender.get('phone')}")
else:
    print(f"Budtender with ID 2098531854 not found")
    
    # Try searching by first name instead
    response2 = supabase.table('budtenders').select('*').ilike('first_name', '%Jocelyn%').execute()
    if response2.data:
        print("\nFound budtender(s) with name 'Jocelyn':")
        for bt in response2.data:
            print(f"  - {bt.get('first_name')} {bt.get('last_name')} (ID: {bt.get('id')}, Points: {bt.get('points', 0)})")
    else:
        print("No budtender named Jocelyn found either")



