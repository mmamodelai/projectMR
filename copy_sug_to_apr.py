#!/usr/bin/env python3
"""
Copy a random SUG message to a test phone and mark it APR for testing
"""
import sys
from supabase import create_client
import json
import random

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Get phone and name from command line or use defaults
if len(sys.argv) >= 3:
    target_phone = sys.argv[1]
    target_name = sys.argv[2]
else:
    target_phone = '+16199773020'
    target_name = 'Stephen Clare (Test)'

print("="*70)
print(f"COPY RANDOM SUG MESSAGE TO {target_name} (APR)")
print("="*70)
print(f"Target: {target_phone}")

# Get all SUG messages
response = supabase.table('campaign_messages').select('*').eq('status', 'SUG').execute()
print(f"\nFound {len(response.data)} SUG messages")

if not response.data:
    print("No SUG messages found!")
    exit(1)

# Pick a random one
random_msg = random.choice(response.data)
print(f"\nSelected message for: {random_msg.get('customer_name')} ({random_msg.get('campaign_name')})")
print(f"Original phone: {random_msg.get('phone_number')}")

# Preview message
msg_content = random_msg.get('message_content', '')
bubbles = msg_content.split('[BUBBLE]')
print(f"\nMessage preview ({len(bubbles)} bubbles):")
for i, bubble in enumerate(bubbles[:3], 1):
    print(f"  Bubble {i}: {bubble.strip()[:60]}...")

# Create new entry with status APR
new_entry = {
    'customer_id': f'test_{target_phone}',
    'customer_name': target_name,
    'phone_number': target_phone,
    'customer_segment': random_msg.get('customer_segment'),
    'message_content': random_msg.get('message_content'),
    'strategy_type': random_msg.get('strategy_type'),
    'confidence': random_msg.get('confidence'),
    'reasoning': random_msg.get('reasoning'),
    'campaign_name': random_msg.get('campaign_name'),
    'campaign_batch_id': 'TEST_BATCH',
    'status': 'APR',  # Already approved!
    'reviewed_by': 'Automated Test',
    'reviewed_at': 'now()',
    'feedback_notes': 'Testing real budtender message with batch scheduler'
}

# Insert
result = supabase.table('campaign_messages').insert(new_entry).execute()
print(f"\n[SUCCESS] Created new APR message (ID: {result.data[0].get('id')})")
print(f"Phone: {target_phone}")
print(f"Name: {target_name}")
print(f"Status: APR (ready for scheduling)")
print(f"Campaign: {random_msg.get('campaign_name')}")

print("\n" + "="*70)
print("READY TO SCHEDULE!")
print("Run: python test_campaign_scheduler.py")
print("="*70)

