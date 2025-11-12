#!/usr/bin/env python3
"""
Check recent incoming messages in Supabase
"""
import json
from datetime import datetime, timedelta
from supabase import create_client, Client

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

db_config = config['database']
supabase: Client = create_client(db_config['supabase_url'], db_config['supabase_key'])

print("\n" + "="*60)
print("RECENT INCOMING MESSAGES CHECK")
print("="*60)

# Get messages from last hour
one_hour_ago = (datetime.now() - timedelta(hours=1)).isoformat()

try:
    # Get recent inbound messages
    response = supabase.table("messages").select("*").eq("direction", "inbound").gte("timestamp", one_hour_ago).order("timestamp", desc=True).limit(10).execute()
    
    messages = response.data
    
    if messages:
        print(f"\n[FOUND] {len(messages)} incoming message(s) in last hour:")
        print()
        for msg in messages:
            phone = msg['phone_number']
            content = msg['content'][:50] + "..." if len(msg['content']) > 50 else msg['content']
            timestamp = msg['timestamp']
            status = msg['status']
            print(f"  {timestamp}")
            print(f"  From: {phone}")
            print(f"  Status: {status}")
            print(f"  Message: {content}")
            print()
    else:
        print("\n[NONE] No incoming messages in last hour")
        print()
        print("Possible reasons:")
        print("  1. Messages still in transit (carrier delay)")
        print("  2. Modem not receiving (but signal is good)")
        print("  3. Messages went to a different number")
        print()
    
    # Check last inbound message of any age
    response = supabase.table("messages").select("*").eq("direction", "inbound").order("timestamp", desc=True).limit(1).execute()
    
    if response.data:
        last = response.data[0]
        last_time = datetime.fromisoformat(last['timestamp'].replace('Z', '+00:00'))
        now = datetime.now(last_time.tzinfo)
        ago = now - last_time
        
        print(f"=== LAST INCOMING MESSAGE ===")
        print(f"From: {last['phone_number']}")
        print(f"Time: {last['timestamp']}")
        print(f"Ago: {ago.total_seconds()/60:.1f} minutes")
        print(f"Content: {last['content'][:100]}")
        print()
    
    # Check outbound (verify system is working)
    response = supabase.table("messages").select("id").eq("direction", "outbound").gte("timestamp", one_hour_ago).execute()
    outbound_count = len(response.data)
    
    print(f"=== SYSTEM HEALTH ===")
    print(f"Outbound messages (last hour): {outbound_count}")
    if outbound_count > 0:
        print("[OK] System is SENDING successfully")
    else:
        print("[WARNING] No outbound messages in last hour")
    print()
    
except Exception as e:
    print(f"\n[ERROR] Database error: {e}")
    print()

print("="*60)
print()
print("To see more: Open DB Viewer (start_db_viewer.bat)")
print()

