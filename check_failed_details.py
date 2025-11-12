#!/usr/bin/env python3
from supabase import create_client
import json
from datetime import datetime

# Load config
with open('conductor-sms/config.json') as f:
    config = json.load(f)

# Init Supabase
supabase = create_client(
    config['database']['supabase_url'],
    config['database']['supabase_key']
)

# Get failed message 396
response = supabase.table('messages').select('*').eq('id', 396).execute()

if response.data:
    msg = response.data[0]
    print("Message 396 Details:")
    print("="*70)
    print(f"  Phone: {msg.get('phone_number')}")
    print(f"  Content: {msg.get('content')}")
    print(f"  Status: {msg.get('status')}")
    print(f"  Retry Count: {msg.get('retry_count')}")
    print(f"  Direction: {msg.get('direction')}")
    print(f"  Timestamp (created): {msg.get('timestamp')}")
    print(f"  Updated At: {msg.get('updated_at')}")
    print(f"  Error Message: {msg.get('error_message', 'N/A')}")
    print()
    
    # Calculate time since last attempt
    if msg.get('updated_at'):
        last_attempt = datetime.fromisoformat(msg['updated_at'].replace('Z', '+00:00'))
        now = datetime.now()
        time_since = (now - last_attempt.replace(tzinfo=None)).total_seconds()
        print(f"Time since last attempt: {time_since:.0f} seconds ({time_since/60:.1f} minutes)")
        
        # Calculate required delay
        base_delay = 30
        retry_count = msg.get('retry_count', 0)
        retry_delay = base_delay * (2 ** (retry_count - 1))
        print(f"Required delay (exponential backoff): {retry_delay} seconds")
        print(f"Should retry? {time_since >= retry_delay}")
else:
    print("Message 396 not found")




