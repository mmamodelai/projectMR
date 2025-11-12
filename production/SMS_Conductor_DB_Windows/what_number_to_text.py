#!/usr/bin/env python3
"""
Figure out what number customers should text TO
"""
import json
from supabase import create_client, Client

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

db_config = config['database']
supabase: Client = create_client(db_config['supabase_url'], db_config['supabase_key'])

print("\n" + "="*60)
print("WHAT NUMBER SHOULD YOU TEXT?")
print("="*60)

# Get the most recent inbound message to see what number people are texting
response = supabase.table("messages").select("*").eq("direction", "inbound").order("timestamp", desc=True).limit(1).execute()

if response.data:
    msg = response.data[0]
    print(f"\nMost recent inbound message:")
    print(f"  From: {msg['phone_number']}")
    print(f"  Time: {msg['timestamp']}")
    print(f"  Message: {msg['content'][:60]}")
    print()
    print("NOTE: This person successfully texted TO our modem number.")
    print("They didn't need to know the number - the system received it.")
    print()

# Get recent OUTBOUND to see what number we're sending FROM
response = supabase.table("messages").select("phone_number").eq("direction", "outbound").order("timestamp", desc=True).limit(10).execute()

print("Recent outbound messages went TO these numbers:")
numbers = set()
for msg in response.data:
    numbers.add(msg['phone_number'])

for num in sorted(numbers):
    print(f"  {num}")

print()
print("="*60)
print("POSSIBLE ISSUES:")
print("="*60)
print()
print("1. TWO-WAY SMS NOT ENABLED on SIM")
print("   - Some data-only SIMs can SEND but not RECEIVE SMS")
print("   - Check Mint Mobile account settings")
print()
print("2. WRONG NUMBER")
print("   - Check what number shows up when WE text YOU")
print("   - Reply to THAT exact number")
print()
print("3. CARRIER BLOCK")
print("   - Your carrier (T-Mobile for 619 area) might block")
print("   - Try from a different phone/carrier")
print()
print("4. MESSAGE ROUTING CHANGED")
print("   - Worked until Nov 9")
print("   - Something changed in carrier routing")
print()
print("="*60)
print("IMMEDIATE TEST:")
print("="*60)
print()
print("1. Check the SENDER on your phone when you receive:")
print("   'TESTING OUTPUT' (sent today at 10:17 AM)")
print()
print("2. Reply DIRECTLY to that message thread")
print("   (Don't create new message)")
print()
print("3. Watch Conductor window for incoming")
print()
print("4. If STILL doesn't work:")
print("   - Have someone else text the same number from THEIR phone")
print("   - If THEIR message works, it's YOUR phone/carrier")
print()

