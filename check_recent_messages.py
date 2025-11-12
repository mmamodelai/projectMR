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
print("RECENT MESSAGES TO +16199773020")
print("="*70)

# Get recent messages
response = supabase.table('messages').select('*').eq('phone_number', '+16199773020').eq('direction', 'outbound').order('id', desc=True).limit(10).execute()

print(f"\nRecent outbound messages: {len(response.data)}")
for msg in response.data[:5]:
    content = msg.get('content', '').encode('ascii', 'ignore').decode()
    print(f"\nID {msg.get('id')}: {msg.get('status')}")
    print(f"  Content: {content[:100]}")
    print(f"  Timestamp: {msg.get('timestamp')}")

