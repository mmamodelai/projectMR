#!/usr/bin/env python3
"""
Check pattern of incoming messages to diagnose intermittent issue
"""
import json
from supabase import create_client
from datetime import datetime, timedelta

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

db_config = config['database']
supabase = create_client(db_config['supabase_url'], db_config['supabase_key'])

print("\n" + "="*70)
print("DIAGNOSING INTERMITTENT INCOMING MESSAGE ISSUE")
print("="*70)

# Get last 20 inbound messages
response = supabase.table("messages").select("*").eq("direction", "inbound").order("timestamp", desc=True).limit(20).execute()

messages = response.data

if not messages:
    print("\n[ERROR] No inbound messages found!")
    exit(1)

print(f"\n[FOUND] {len(messages)} recent inbound messages")
print()

# Group by time gaps
print("=== TIMING ANALYSIS ===")
print()
last_time = None
gaps = []

for msg in reversed(messages):  # Oldest first
    time = datetime.fromisoformat(msg['timestamp'].replace('Z', '+00:00'))
    phone = msg['phone_number'][-4:]
    content = msg['content'][:30]
    
    if last_time:
        gap = (time - last_time).total_seconds()
        gaps.append(gap)
        gap_str = f"{gap:.0f}s" if gap < 120 else f"{gap/60:.1f}m"
        print(f"  [{gap_str:>8}] {time.strftime('%H:%M:%S')} | {phone} | {content}")
    else:
        print(f"  [  START] {time.strftime('%H:%M:%S')} | {phone} | {content}")
    
    last_time = time

print()
print("=== STATISTICS ===")
if gaps:
    print(f"Average gap: {sum(gaps)/len(gaps):.1f} seconds")
    print(f"Min gap: {min(gaps):.1f}s")
    print(f"Max gap: {max(gaps):.1f}s")
    print(f"Gaps > 5 min: {len([g for g in gaps if g > 300])}")

print()
print("=== CHECKING FOR YOUR TEST MESSAGES ===")
print()

# Check for messages from user's numbers
user_numbers = ["+16199773020", "+16232301086"]  # User's cell and others
recent_cutoff = datetime.now(datetime.now().astimezone().tzinfo) - timedelta(hours=2)

for num in user_numbers:
    response = supabase.table("messages").select("*").eq("phone_number", num).eq("direction", "inbound").gte("timestamp", recent_cutoff.isoformat()).order("timestamp", desc=True).execute()
    
    if response.data:
        print(f"\nFrom {num}:")
        for msg in response.data:
            time = datetime.fromisoformat(msg['timestamp'].replace('Z', '+00:00'))
            print(f"  {time.strftime('%I:%M %p')} - {msg['content'][:50]}")
    else:
        print(f"\nFrom {num}: No messages in last 2 hours")

print()
print("=== POSSIBLE CAUSES OF INTERMITTENT DELIVERY ===")
print()
print("1. Timing: Messages arriving during 0.26s COM port lock")
print("   - Very unlikely (99.5% uptime)")
print()
print("2. Duplicate detection: Messages falsely detected as duplicates")
print("   - Check if test messages have same content")
print()
print("3. Storage race condition: Message deleted before read")
print("   - Would show in logs as 'Duplicate message'")
print()
print("4. Network/Carrier: Some messages delayed or dropped")
print("   - Test with different carriers/phones")
print()
print("5. Modem firmware: Bug in message notification")
print("   - Some messages don't trigger +CMTI")
print()

# Check if any messages were marked as duplicates recently
print("=== CHECKING LOGS FOR DUPLICATE WARNINGS ===")
print()
try:
    with open('logs/conductor_system.log', 'r') as f:
        lines = f.readlines()
        dup_lines = [l for l in lines[-1000:] if 'Duplicate' in l and 'inbound' in l.lower()]
        if dup_lines:
            print(f"Found {len(dup_lines)} duplicate warnings:")
            for line in dup_lines[-5:]:
                print(f"  {line.strip()}")
        else:
            print("No duplicate warnings found")
except Exception as e:
    print(f"Could not read logs: {e}")

print()

