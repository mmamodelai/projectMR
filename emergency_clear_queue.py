#!/usr/bin/env python3
"""
Emergency: Clear the queued message flood
"""
from supabase import create_client

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("="*70)
print("EMERGENCY: CLEARING QUEUED MESSAGES")
print("="*70)

# Get queued count
response = supabase.table('messages').select('id', count='exact').eq('status', 'queued').execute()
count = len(response.data)

print(f"\nFound {count} queued messages")
print("These are from the mass-queue accident at 2:14 PM")
print("\nDeleting them to prevent flood when Conductor restarts...")

# Delete all queued messages
result = supabase.table('messages').delete().eq('status', 'queued').execute()

print(f"\n✓ Deleted {count} queued messages")
print("\nQueue is now clear. Safe to restart Conductor.")
print("="*70)

