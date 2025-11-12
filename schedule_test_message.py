#!/usr/bin/env python3
"""
Schedule a test message for 11:47 AM PST on November 8, 2025
"""
from supabase import create_client
from datetime import datetime
import pytz

# Supabase connection
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Create PST timezone
pst = pytz.timezone('America/Los_Angeles')

# Target time: 11:47 AM PST on November 8, 2025
target_pst = pst.localize(datetime(2025, 11, 8, 11, 47, 0))

# Convert to UTC for storage
target_utc = target_pst.astimezone(pytz.UTC)

print("="*70)
print("SCHEDULING TEST MESSAGE")
print("="*70)
print(f"Phone: +16199773020")
print(f"Scheduled for (PST): {target_pst.strftime('%Y-%m-%d %I:%M %p %Z')}")
print(f"Scheduled for (UTC): {target_utc.strftime('%Y-%m-%d %I:%M %p %Z')}")
print()

# Test message content (3 bubbles)
test_content = """Test bubble 1: This is a test of the scheduling system at 11:47 AM PST.

[BUBBLE]

Test bubble 2: If you receive this, the Pacific Time scheduling is working correctly!

[BUBBLE]

Test bubble 3: This message was scheduled via the database-native scheduler."""

try:
    # Insert into scheduled_messages
    response = supabase.table('scheduled_messages').insert({
        'phone_number': '+16199773020',
        'customer_name': 'Stephen Clare (Test)',
        'message_content': test_content,
        'scheduled_for': target_utc.isoformat(),
        'status': 'SCH',
        'campaign_name': 'test_11_47_am',
        'created_at': datetime.utcnow().isoformat()
    }).execute()
    
    msg_id = response.data[0]['id']
    
    print("[OK] Test message scheduled!")
    print(f"Message ID: {msg_id}")
    print()
    print("What happens next:")
    print("1. At 11:47 AM PST, Supabase pg_cron will process this")
    print("2. It will split into 3 bubbles and queue in 'messages' table")
    print("3. Conductor will send within 10 seconds")
    print("4. You'll receive 3 separate SMS messages")
    print()
    print("To cancel:")
    print(f"  UPDATE scheduled_messages SET status='cancelled' WHERE id={msg_id};")
    print("="*70)

except Exception as e:
    print(f"[ERROR] {e}")

