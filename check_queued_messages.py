#!/usr/bin/env python3
from supabase import create_client
import json

# Load config
with open('conductor-sms/config.json') as f:
    config = json.load(f)

supabase = create_client(
    config['database']['supabase_url'],
    config['database']['supabase_key']
)

print("="*70)
print("QUEUED MESSAGES")
print("="*70)

# Get queued messages
response = supabase.table('messages').select('*').eq('status', 'queued').eq('direction', 'outbound').order('id').execute()

print(f"\nQueued messages: {len(response.data)}")
for msg in response.data:
    print(f"\nID {msg.get('id')}: {msg.get('phone_number')}")
    print(f"  Content: {msg.get('content')}")
    print(f"  Timestamp: {msg.get('timestamp')}")
    print(f"  Status: {msg.get('status')}")

