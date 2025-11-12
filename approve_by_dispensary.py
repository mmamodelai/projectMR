#!/usr/bin/env python3
"""
Approve campaign messages by dispensary
"""
from supabase import create_client
import json
import sys

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("="*70)
print("APPROVE CAMPAIGNS BY DISPENSARY")
print("="*70)

# Get all SUG messages
response = supabase.table('campaign_messages').select('*').eq('status', 'SUG').execute()
print(f"\nTotal SUG messages: {len(response.data)}")

# Group by dispensary
dispensaries = {}
for msg in response.data:
    reasoning = msg.get('reasoning', '{}')
    try:
        reasoning_data = json.loads(reasoning) if isinstance(reasoning, str) else reasoning
        dispensary = reasoning_data.get('dispensary_name', 'Unknown')
    except:
        dispensary = 'Unknown'
    
    if dispensary not in dispensaries:
        dispensaries[dispensary] = []
    dispensaries[dispensary].append(msg)

# Sort by count
sorted_dispensaries = sorted(dispensaries.items(), key=lambda x: len(x[1]), reverse=True)

print(f"\n{'Dispensary':<40} {'Messages':>10}")
print("-" * 70)
for dispensary, msgs in sorted_dispensaries:
    print(f"{dispensary:<40} {len(msgs):>10}")

# If dispensary name provided, approve those messages
if len(sys.argv) > 1:
    target_dispensary = ' '.join(sys.argv[1:])
    
    print("\n" + "="*70)
    print(f"APPROVING: {target_dispensary}")
    print("="*70)
    
    if target_dispensary not in dispensaries:
        print(f"\nERROR: Dispensary '{target_dispensary}' not found!")
        print("\nAvailable dispensaries:")
        for disp, _ in sorted_dispensaries:
            print(f"  - {disp}")
        sys.exit(1)
    
    messages_to_approve = dispensaries[target_dispensary]
    print(f"\nApproving {len(messages_to_approve)} messages for {target_dispensary}...")
    
    # Get IDs
    ids = [msg['id'] for msg in messages_to_approve]
    
    # Update to APR
    result = supabase.table('campaign_messages').update({
        'status': 'APR',
        'reviewed_by': 'Manual Approval (by dispensary)',
        'reviewed_at': 'now()',
        'feedback_notes': f'Approved dispensary batch: {target_dispensary}'
    }).in_('id', ids).execute()
    
    print(f"\n[SUCCESS] Approved {len(ids)} messages!")
    print(f"Status: SUG -> APR")
    print(f"Dispensary: {target_dispensary}")
    
    print("\n" + "="*70)
    print("NEXT STEP: Schedule them!")
    print("Run: python test_campaign_scheduler.py")
    print("="*70)
    
else:
    print("\n" + "="*70)
    print("USAGE:")
    print("  python approve_by_dispensary.py \"Dispensary Name\"")
    print("\nExample:")
    print("  python approve_by_dispensary.py \"Higher Level\"")
    print("="*70)

