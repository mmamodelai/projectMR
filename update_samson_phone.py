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

# Search for Samson T
response = supabase.table('budtenders').select('*').ilike('first_name', 'Samson').execute()

print(f"Found {len(response.data)} budtenders named Samson")
print("="*70)

for budtender in response.data:
    if budtender['last_name'].startswith('T'):
        print(f"\nFound: {budtender['first_name']} {budtender['last_name']}")
        print(f"  ID: {budtender['id']}")
        print(f"  Dispensary: {budtender['dispensary_name']}")
        print(f"  Current Phone: {budtender.get('phone', 'N/A')}")
        print(f"  Email: {budtender.get('email', 'N/A')}")
        print(f"  Points: {budtender['points']}")
        
        # Update phone number
        new_phone = "+16195587489"
        print(f"\nUpdating phone to: {new_phone}")
        
        update_response = supabase.table('budtenders').update({
            'phone': new_phone
        }).eq('id', budtender['id']).execute()
        
        print("✓ Phone number updated successfully!")
        break
else:
    print("\nSamson T not found in database")



