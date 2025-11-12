#!/usr/bin/env python3
"""
Check for expired campaign messages that need manual review
"""
from supabase import create_client
import json

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("="*70)
print("EXPIRED MESSAGES - MANUAL REVIEW NEEDED")
print("="*70)

# Get expired messages
response = supabase.table('campaign_messages').select('*').eq('status', 'expired').execute()

if not response.data:
    print("\nNo expired messages. All good!")
else:
    print(f"\nFound {len(response.data)} expired messages:")
    print("-" * 70)
    
    for msg in response.data:
        name = msg.get('customer_name', '').encode('ascii', 'ignore').decode()
        phone = msg.get('phone_number')
        scheduled = msg.get('scheduled_for', '')
        feedback = msg.get('feedback_notes', '')
        
        reasoning = msg.get('reasoning', '{}')
        try:
            reasoning_data = json.loads(reasoning) if isinstance(reasoning, str) else reasoning
            dispensary = reasoning_data.get('dispensary_name', 'Unknown')
        except:
            dispensary = 'Unknown'
        
        print(f"\n  {name:<30} ({dispensary})")
        print(f"    Phone: {phone}")
        print(f"    Scheduled: {scheduled}")
        if feedback:
            print(f"    Reason: {feedback[-100:]}")  # Last 100 chars

print("\n" + "="*70)
print("To reschedule these messages:")
print("  1. Review each one manually")
print("  2. Change status from 'expired' to 'APR'")
print("  3. Run scheduler again to assign new time")
print("="*70)

