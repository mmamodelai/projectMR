#!/usr/bin/env python3
"""
Test the campaign scheduler functions
"""
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
print("CAMPAIGN SCHEDULER TEST")
print("="*70)

# Check business hours
print("\n1. Checking business hours status...")
result = supabase.table('business_hours_status').select('*').execute()
if result.data:
    status = result.data[0]
    print(f"   Current Time (PST): {status.get('current_time_pst')}")
    print(f"   Is Open: {status.get('is_open')}")
    print(f"   Status: {status.get('status')}")

# Schedule APR messages
print("\n2. Scheduling APR messages...")
result = supabase.rpc('schedule_approved_messages').execute()
print(f"   Result: {result.data}")

# Check scheduled messages
print("\n3. Checking scheduled messages...")
result = supabase.table('scheduled_messages_view').select('*').limit(10).execute()
print(f"   Scheduled: {len(result.data)} messages")
for msg in result.data[:5]:
    name = msg.get('customer_name', '').encode('ascii', 'ignore').decode()
    print(f"   - {name} at {msg.get('scheduled_pst')}")

# Process scheduled messages (queue them if time arrived)
print("\n4. Processing scheduled messages (move to queue if ready)...")
result = supabase.rpc('process_scheduled_messages').execute()
print(f"   Result: {result.data}")

print("\n" + "="*70)
print("DONE! Check SMS Viewer or messages table to see queued messages")
print("="*70)

