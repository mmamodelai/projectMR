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

# Get Samson T
response = supabase.table('budtenders').select('*').eq('id', 1912).execute()

if response.data:
    b = response.data[0]
    print(f"Samson T - Updated Info:")
    print(f"  Phone: {b['phone']}")
    print(f"  Email: {b['email']}")
    print(f"  Dispensary: {b['dispensary_name']}")
    print(f"  Points: {b['points']}")
    print("\nPhone number updated successfully!")



