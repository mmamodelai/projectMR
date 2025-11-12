#!/usr/bin/env python3
"""
Reschedule the 29 Flavors budtenders who never got messages
Leave the 9 who already got messages alone
"""
from supabase import create_client
import json

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("="*70)
print("RESCHEDULE UNSENT FLAVORS BUDTENDERS")
print("="*70)

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

print(f"\nTotal Flavors campaigns: {len(flavors_msgs)}")

# Check which ones actually got messages sent
unsent = []
already_sent = []

for msg in flavors_msgs:
    phone = msg.get('phone_number')
    name = msg.get('customer_name')
    msg_id = msg.get('id')
    
    # Check if ANY messages sent to this phone
    response = supabase.table('messages').select('id').eq('phone_number', phone).eq('direction', 'outbound').eq('status', 'sent').execute()
    
    if len(response.data) > 0:
        already_sent.append({'id': msg_id, 'name': name, 'phone': phone})
    else:
        unsent.append({'id': msg_id, 'name': name, 'phone': phone})

print(f"\n  Already sent: {len(already_sent)} (will leave as 'sent')")
print(f"  Not sent:     {len(unsent)} (will change to 'APR' and reschedule)")

# Show who's getting rescheduled
print(f"\n{'='*70}")
print(f"RESCHEDULING THESE {len(unsent)} BUDTENDERS:")
print(f"{'='*70}")
for person in unsent[:10]:
    name = person['name'].encode('ascii', 'ignore').decode()
    print(f"  {name}")
if len(unsent) > 10:
    print(f"  ... and {len(unsent) - 10} more")

# Confirm
print(f"\n{'='*70}")
print("This will:")
print(f"  1. Change {len(unsent)} campaigns from 'sent' -> 'APR'")
print(f"  2. Leave {len(already_sent)} campaigns as 'sent' (don't resend)")
print(f"  3. Clear old scheduled_for timestamps")
print(f"  4. Ready to run scheduler for NEW times starting NOW")
print(f"{'='*70}")

confirm = input("\nProceed? (yes/no): ").strip().lower()

if confirm != 'yes':
    print("\nAborted. No changes made.")
    exit(0)

# Update unsent to APR status
unsent_ids = [p['id'] for p in unsent]

print(f"\nChanging {len(unsent_ids)} campaigns to APR status...")

result = supabase.table('campaign_messages').update({
    'status': 'APR',
    'scheduled_for': None,  # Clear old timestamp
    'feedback_notes': 'Rescheduled after processing failure - never sent',
    'updated_at': 'now()'
}).in_('id', unsent_ids).execute()

print(f"\n[SUCCESS] {len(unsent_ids)} campaigns ready to reschedule!")

print(f"\n{'='*70}")
print("NEXT STEP:")
print("  Run: python test_campaign_scheduler.py")
print("  This will assign NEW times starting from NOW")
print(f"{'='*70}")

