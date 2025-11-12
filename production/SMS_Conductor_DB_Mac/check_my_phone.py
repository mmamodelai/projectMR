#!/usr/bin/env python3
"""
Check for messages from +16199773020 (user's phone)
"""
import json
from supabase import create_client, Client
from datetime import datetime

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

db_config = config['database']
supabase: Client = create_client(db_config['supabase_url'], db_config['supabase_key'])

MY_PHONE = "+16199773020"

print("\n" + "="*60)
print(f"INVESTIGATING: {MY_PHONE}")
print("="*60)

# Check ALL messages from this number
response = supabase.table("messages").select("*").eq("phone_number", MY_PHONE).order("timestamp", desc=True).limit(20).execute()

messages = response.data

if messages:
    print(f"\n[FOUND] {len(messages)} message(s) from this number:\n")
    for msg in messages:
        print(f"ID: {msg['id']}")
        print(f"Direction: {msg['direction']}")
        print(f"Status: {msg['status']}")
        print(f"Time: {msg['timestamp']}")
        print(f"Content: {msg['content'][:80]}")
        print()
else:
    print(f"\n[NONE] NO messages found from {MY_PHONE}")
    print("\n🚨 THIS IS THE PROBLEM!")
    print("Your phone number has NEVER sent a message to this system.")
    print()

# Check recent INBOUND from ANY number
print("\n" + "="*60)
print("RECENT INBOUND FROM OTHERS (for comparison):")
print("="*60)

response = supabase.table("messages").select("*").eq("direction", "inbound").order("timestamp", desc=True).limit(5).execute()

for msg in response.data:
    time_obj = datetime.fromisoformat(msg['timestamp'].replace('Z', '+00:00'))
    print(f"{msg['phone_number']}: {msg['content'][:50]}")
    print(f"  Time: {time_obj.strftime('%I:%M %p')}")
    print()

# Check recent OUTBOUND to user's phone
print("\n" + "="*60)
print(f"OUTBOUND TO {MY_PHONE}:")
print("="*60)

response = supabase.table("messages").select("*").eq("phone_number", MY_PHONE).eq("direction", "outbound").order("timestamp", desc=True).limit(5).execute()

if response.data:
    print(f"\n[FOUND] {len(response.data)} outbound message(s):\n")
    for msg in response.data:
        time_obj = datetime.fromisoformat(msg['timestamp'].replace('Z', '+00:00'))
        print(f"Status: {msg['status']}")
        print(f"Time: {time_obj.strftime('%I:%M %p')}")
        print(f"Content: {msg['content'][:60]}")
        print()
    print("[OK] System CAN send TO your phone")
else:
    print("\n[NONE] No outbound messages to this number")

print("\n" + "="*60)
print("DIAGNOSIS:")
print("="*60)
print()
print("If NO inbound messages from your phone:")
print("  🚨 CARRIER/NETWORK ISSUE")
print("  - Your messages aren't reaching the modem")
print("  - Check:")
print(f"    1. Are you texting the RIGHT number?")
print("    2. Is your number blocked by carrier?")
print("    3. Try from a DIFFERENT phone to same modem number")
print()
print("If inbound messages exist but STOPPED recently:")
print("  - Check message timestamps")
print("  - Look for pattern in when they stopped")
print()

