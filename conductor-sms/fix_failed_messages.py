#!/usr/bin/env python3
"""
Fix Failed Messages from CGSMS Issue
Mark messages that were sent during the circuit-switched issue as failed
"""
from supabase import create_client
from datetime import datetime

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

# Message IDs that failed to deliver (before CGSMS fix at 11:12 AM)
FAILED_MESSAGE_IDS = [478, 479, 480, 481, 482, 485, 487, 488]

def main():
    print("=" * 80)
    print("FIXING FAILED MESSAGES FROM CGSMS ISSUE")
    print("=" * 80)
    print()
    
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    print(f"Marking {len(FAILED_MESSAGE_IDS)} messages as 'failed'...")
    print(f"IDs: {FAILED_MESSAGE_IDS}")
    print()
    
    for msg_id in FAILED_MESSAGE_IDS:
        try:
            result = supabase.table('messages').update({
                'status': 'failed',
                'updated_at': datetime.utcnow().isoformat()
            }).eq('id', msg_id).execute()
            
            if result.data:
                print(f"[OK] Message ID {msg_id} marked as failed")
            else:
                print(f"[SKIP] Message ID {msg_id} not found or already updated")
        except Exception as e:
            print(f"[ERROR] Error updating message ID {msg_id}: {e}")
    
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    # Get updated counts
    try:
        failed_count = supabase.table('messages').select('id', count='exact').eq('status', 'failed').execute()
        sent_count = supabase.table('messages').select('id', count='exact').eq('status', 'sent').execute()
        
        print(f"Failed messages: {failed_count.count}")
        print(f"Sent messages: {sent_count.count}")
        print()
        print("These failed messages were sent during the CGSMS=1 issue (6:52 AM - 11:12 AM)")
        print("They showed as 'sent' but never delivered due to carrier rejecting circuit-switched SMS")
        print()
        print("[OK] Database now reflects actual delivery status")
    except Exception as e:
        print(f"Error getting summary: {e}")

if __name__ == "__main__":
    main()

