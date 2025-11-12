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

# Get failed messages
response = supabase.table('messages').select('*').eq('status', 'failed').lt('retry_count', 5).order('id').execute()

print(f"Failed messages eligible for retry: {len(response.data)}")
print("="*70)

for msg in response.data:
    print(f"\nID: {msg.get('id')}")
    print(f"  Phone: {msg.get('phone_number')}")
    print(f"  Content: {msg.get('content')[:50]}...")
    print(f"  Status: {msg.get('status')}")
    print(f"  Retry Count: {msg.get('retry_count')}")
    print(f"  Direction: {msg.get('direction')}")
    print(f"  Timestamp: {msg.get('timestamp')}")
    print(f"  Error: {msg.get('error_message', 'N/A')}")




