#!/usr/bin/env python3
"""
Remove [BUBBLE] markers from all campaign messages
Replace with line breaks for single-message sending
"""
from supabase import create_client

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("="*70)
print("REMOVE [BUBBLE] MARKERS FROM ALL CAMPAIGN MESSAGES")
print("="*70)

# Get all campaign messages with [BUBBLE] markers
response = supabase.table('campaign_messages').select('*').execute()

messages_with_bubbles = []
for msg in response.data:
    content = msg.get('message_content', '')
    if '[BUBBLE]' in content:
        messages_with_bubbles.append(msg)

print(f"\nFound {len(messages_with_bubbles)} messages with [BUBBLE] markers")

if len(messages_with_bubbles) == 0:
    print("\nNothing to clean!")
    exit(0)

# Show a few examples
print("\nExample transformations:")
print("-" * 70)
for msg in messages_with_bubbles[:3]:
    name = msg.get('customer_name', '').encode('ascii', 'ignore').decode()
    old = msg.get('message_content', '')
    new = old.replace('[BUBBLE]', '\n\n')
    bubbles = old.count('[BUBBLE]') + 1
    print(f"\n{name}: {bubbles} bubbles -> 1 message ({len(new)} chars)")
    print(f"  Old: {old[:80]}...")
    print(f"  New: {new[:80]}...")

print("\n" + "="*70)
print(f"This will update {len(messages_with_bubbles)} messages")
print("Replacing [BUBBLE] with line breaks (\\n\\n)")
print("="*70)

# Update each message
updated = 0
for msg in messages_with_bubbles:
    msg_id = msg.get('id')
    old_content = msg.get('message_content', '')
    new_content = old_content.replace('[BUBBLE]', '\n\n')
    
    supabase.table('campaign_messages').update({
        'message_content': new_content
    }).eq('id', msg_id).execute()
    
    updated += 1
    if updated % 10 == 0:
        print(f"  Updated {updated}/{len(messages_with_bubbles)}...")

print(f"\n[SUCCESS] Updated {updated} messages!")
print("All campaign messages now use single-send format")
print("="*70)

