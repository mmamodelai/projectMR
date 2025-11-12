#!/usr/bin/env python3
"""Inspect campaign_messages table structure"""

from supabase import create_client
import json

CRM_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
CRM_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

sb = create_client(CRM_URL, CRM_KEY)

print("=" * 80)
print("CAMPAIGN_MESSAGES TABLE STRUCTURE")
print("=" * 80)

# Get sample row
result = sb.table('campaign_messages').select('*').limit(1).execute()

if result.data:
    row = result.data[0]
    print("\nCOLUMNS:")
    for key, value in row.items():
        val_preview = str(value)[:60] if value else 'NULL'
        print(f"  {key:25} = {val_preview}")
    
    print("\n" + "=" * 80)
    print("FULL SAMPLE ROW:")
    print("=" * 80)
    print(json.dumps(row, indent=2, default=str))

# Get total count
count_result = sb.table('campaign_messages').select('id', count='exact').execute()
print(f"\nTOTAL ROWS: {count_result.count if hasattr(count_result, 'count') else 'Unknown'}")

# Get status breakdown
statuses = sb.table('campaign_messages').select('status').execute()
if statuses.data:
    from collections import Counter
    status_counts = Counter([s.get('status') for s in statuses.data])
    print("\nSTATUS BREAKDOWN:")
    for status, count in status_counts.items():
        print(f"  {status}: {count}")

