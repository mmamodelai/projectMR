#!/usr/bin/env python3
"""Find budtender campaign tables in Supabase"""

from supabase import create_client

CRM_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
CRM_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

sb = create_client(CRM_URL, CRM_KEY)

print("Searching for budtender campaign tables...\n")

# Try common variations
table_names = [
    'budtender_campaigns',
    'bt_campaigns',
    'external_campaigns',
    'budtender_messages',
    'bt_campaign_messages',
    'campaign_messages_bt',
    'budtender_outreach',
    'external_budtender_campaigns'
]

for table_name in table_names:
    try:
        result = sb.table(table_name).select('*').limit(3).execute()
        print(f"[FOUND] {table_name}")
        if result.data:
            print(f"  Columns: {', '.join(result.data[0].keys())}")
            print(f"  Sample messages:")
            for msg in result.data:
                content = msg.get('message_content') or msg.get('content') or msg.get('message') or 'N/A'
                print(f"    - {content[:80]}...")
    except Exception as e:
        if 'not found' not in str(e).lower():
            print(f"[ERROR] {table_name}: {e}")

# Also search campaign_messages for budtender-specific content
print("\n[Searching campaign_messages for budtender content]")
try:
    result = sb.table('campaign_messages').select('*').limit(100).execute()
    if result.data:
        budtender_msgs = []
        for msg in result.data:
            content = str(msg.get('message_content', '')).lower()
            if any(word in content for word in ['budtender', 't-shirt', 'shirt', 'external', 'points', 'dispensary']):
                budtender_msgs.append(msg)
        
        if budtender_msgs:
            print(f"  Found {len(budtender_msgs)} budtender-related messages:")
            for msg in budtender_msgs[:5]:
                print(f"    ID {msg.get('id')}: {msg.get('message_content', '')[:80]}...")
                if msg.get('phone_number'):
                    print(f"      To: {msg.get('phone_number')}")
        else:
            print("  No budtender-related content found in campaign_messages")
except Exception as e:
    print(f"  Error: {e}")

