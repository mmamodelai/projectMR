#!/usr/bin/env python3
"""
Show scheduled messages timeline
"""
from supabase import create_client
import json
from datetime import datetime

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("="*80)
print("SCHEDULED MESSAGES TIMELINE")
print("="*80)

# Get all scheduled messages
response = supabase.table('campaign_messages').select('*').eq('status', 'SCH').order('scheduled_for').execute()

print(f"\nTotal scheduled: {len(response.data)} messages")

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

print(f"\nBy Dispensary:")
for disp, msgs in dispensaries.items():
    print(f"  {disp}: {len(msgs)} messages")

print("\n" + "="*80)
print("SCHEDULE TIMELINE (First 20 messages)")
print("="*80)

from datetime import timezone as tz
import pytz

pst = pytz.timezone('America/Los_Angeles')

for i, msg in enumerate(response.data[:20], 1):
    name = msg.get('customer_name', '').encode('ascii', 'ignore').decode()
    scheduled = msg.get('scheduled_for')
    
    # Parse and convert to PST
    dt = datetime.fromisoformat(scheduled.replace('Z', '+00:00'))
    dt_pst = dt.astimezone(pst)
    time_str = dt_pst.strftime('%I:%M:%S %p')
    
    reasoning = msg.get('reasoning', '{}')
    try:
        reasoning_data = json.loads(reasoning) if isinstance(reasoning, str) else reasoning
        dispensary = reasoning_data.get('dispensary_name', 'Unknown')
    except:
        dispensary = 'Unknown'
    
    print(f"{i:2}. {time_str} - {name[:30]:<30} ({dispensary})")

if len(response.data) > 20:
    print(f"\n... and {len(response.data) - 20} more")

# Show time range
if response.data:
    first = datetime.fromisoformat(response.data[0]['scheduled_for'].replace('Z', '+00:00')).astimezone(pst)
    last = datetime.fromisoformat(response.data[-1]['scheduled_for'].replace('Z', '+00:00')).astimezone(pst)
    duration = (last - first).total_seconds() / 3600
    
    print("\n" + "="*80)
    print(f"Start time: {first.strftime('%I:%M %p PST')}")
    print(f"End time:   {last.strftime('%I:%M %p PST')}")
    print(f"Duration:   {duration:.1f} hours")
    print("="*80)

