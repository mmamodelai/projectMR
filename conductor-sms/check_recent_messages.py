#!/usr/bin/env python3
"""
Check most recent messages to see what just happened
"""
from supabase import create_client
import json
from datetime import datetime, timedelta

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

sb = create_client(
    config['database']['supabase_url'],
    config['database']['supabase_key']
)

# Get last 20 messages
print("=" * 80)
print("LAST 20 MESSAGES (Most Recent First)")
print("=" * 80)

recent = sb.table('messages').select('*').order('timestamp', desc=True).limit(20).execute()

if not recent.data:
    print("No messages found")
else:
    for i, msg in enumerate(recent.data, 1):
        phone = msg['phone_number'] if msg['phone_number'] else "[EMPTY]"
        content_preview = msg['content'][:50] + "..." if len(msg['content']) > 50 else msg['content']
        timestamp = msg['timestamp']
        
        print(f"\n{i}. [{msg['status'].upper()}] {msg['direction']}")
        print(f"   ID: {msg['id']}")
        print(f"   Phone: {phone}")
        print(f"   Time: {timestamp}")
        print(f"   Content: {content_preview}")

