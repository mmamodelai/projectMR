#!/usr/bin/env python3
"""
Send test message directly from Cursor Agent
"""
from supabase import create_client
import json
from datetime import datetime

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

sb = create_client(
    config['database']['supabase_url'],
    config['database']['supabase_key']
)

# Queue a test message with unique identifier
test_message = {
    'phone_number': '+16199773020',
    'content': 'CURSOR AGENT TEST #2 - If you receive this, normalization is working!',
    'direction': 'outbound',
    'status': 'queued',
    'timestamp': datetime.utcnow().isoformat()
}

print("=" * 80)
print("QUEUING TEST MESSAGE FROM CURSOR AGENT")
print("=" * 80)
print("\nTo: +16199773020")
print("Message: CURSOR AGENT TEST #2")
print("\nQueuing...")

result = sb.table('messages').insert(test_message).execute()

if result.data:
    msg_id = result.data[0]['id']
    print(f"\nSUCCESS! Message queued with ID: {msg_id}")
    print(f"\nConductor will send it within 5 seconds.")
    print(f"Watch for: 'CURSOR AGENT TEST #2' on your phone")
else:
    print("\nFAILED to queue message")

print("=" * 80)

