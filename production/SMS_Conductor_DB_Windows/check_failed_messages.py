#!/usr/bin/env python3
"""
Check failed messages in database
"""
from supabase import create_client
import json

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

sb = create_client(
    config['database']['supabase_url'],
    config['database']['supabase_key']
)

# Get failed messages
print("=" * 80)
print("FAILED MESSAGES")
print("=" * 80)

failed = sb.table('messages').select('*').eq('status', 'failed').order('timestamp', desc=True).execute()

if not failed.data:
    print("No failed messages found")
else:
    print(f"\nFound {len(failed.data)} failed messages:\n")
    for i, msg in enumerate(failed.data, 1):
        print(f"{i}. ID: {msg['id']}")
        print(f"   Phone: {msg['phone_number']}")
        print(f"   Direction: {msg['direction']}")
        print(f"   Content: {msg['content'][:60]}...")
        print(f"   Timestamp: {msg['timestamp']}")
        print()

# Get all messages count
print("=" * 80)
print("ALL STATUS COUNTS")
print("=" * 80)

for status in ['sent', 'failed', 'queued', 'unread', 'read']:
    result = sb.table('messages').select('id', count='exact').eq('status', status).execute()
    print(f"{status}: {result.count}")

