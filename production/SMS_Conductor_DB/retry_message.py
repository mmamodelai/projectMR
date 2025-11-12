#!/usr/bin/env python3
from supabase import create_client
import json

# Load config
with open('config.json') as f:
    config = json.load(f)

# Init Supabase
supabase = create_client(
    config['database']['supabase_url'],
    config['database']['supabase_key']
)

# Find message 383
response = supabase.table('messages').select('*').eq('id', 383).execute()
if response.data:
    msg = response.data[0]
    print(f"Found message 383:")
    print(f"  Status: {msg.get('status')}")
    print(f"  Retry Count: {msg.get('retry_count')}")
    print(f"  Phone: {msg.get('phone_number')}")
    print(f"  Content: {msg.get('content')}")
    
    # Reset retry count to 0 so it retries
    print(f"\nResetting to queued status with retry_count=0...")
    update_response = supabase.table('messages').update({
        'retry_count': 0,
        'status': 'queued'
    }).eq('id', 383).execute()
    print("SUCCESS! Message 383 will retry on next poll cycle")
else:
    print("Message 383 not found")



