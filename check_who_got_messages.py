#!/usr/bin/env python3
"""
Check which Flavors budtenders actually received messages
"""
from supabase import create_client
import json

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("="*80)
print("FLAVORS CAMPAIGN - WHO GOT MESSAGES")
print("="*80)

# Get all Flavors campaign messages
response = supabase.table('campaign_messages').select('*').execute()
flavors_msgs = []
for msg in response.data:
    reasoning = msg.get('reasoning', '{}')
    try:
        reasoning_data = json.loads(reasoning) if isinstance(reasoning, str) else reasoning
        dispensary = reasoning_data.get('dispensary_name', '')
        if dispensary == 'Flavors':
            flavors_msgs.append(msg)
    except:
        pass

print(f"\nTotal Flavors campaign messages: {len(flavors_msgs)}")

# Get all their phone numbers
flavors_phones = set([msg.get('phone_number') for msg in flavors_msgs])

# Check messages table for each phone
sent_to = []
not_sent_to = []

for msg in flavors_msgs:
    phone = msg.get('phone_number')
    name = msg.get('customer_name')
    
    # Check if ANY messages sent to this phone
    response = supabase.table('messages').select('*').eq('phone_number', phone).eq('direction', 'outbound').eq('status', 'sent').execute()
    
    if len(response.data) > 0:
        sent_to.append({'name': name, 'phone': phone, 'bubbles': len(response.data)})
    else:
        not_sent_to.append({'name': name, 'phone': phone})

print(f"\n{'='*80}")
print(f"SUCCESSFULLY SENT: {len(sent_to)} budtenders")
print(f"{'='*80}")
for person in sent_to:
    name = person['name'].encode('ascii', 'ignore').decode()
    print(f"  [SENT] {name:<40} ({person['bubbles']} SMS bubbles)")

print(f"\n{'='*80}")
print(f"NOT SENT (still scheduled): {len(not_sent_to)} budtenders")
print(f"{'='*80}")
for person in not_sent_to:
    name = person['name'].encode('ascii', 'ignore').decode()
    print(f"  [SKIP] {name:<40} {person['phone']}")

print(f"\n{'='*80}")
print("SUMMARY:")
print(f"  Sent:     {len(sent_to)}/{len(flavors_msgs)}")
print(f"  Not Sent: {len(not_sent_to)}/{len(flavors_msgs)}")
print(f"{'='*80}")

