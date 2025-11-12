#!/usr/bin/env python3
"""
Bulk Approve Campaign Messages
Changes status from SUG (suggested) to APR (approved)

Usage:
    python approve_all_campaigns.py --dry-run  # Preview
    python approve_all_campaigns.py            # Actually approve
"""
from supabase import create_client
import sys

# Supabase connection
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def approve_all(dry_run=False):
    """Approve all SUG messages (change to APR)"""
    print("="*70)
    print("BULK APPROVE CAMPAIGN MESSAGES")
    print("="*70)
    print(f"Dry Run: {'YES (no changes)' if dry_run else 'NO (will approve)'}")
    print()
    
    # Query SUG messages
    response = supabase.table('campaign_messages').select('*').eq('status', 'SUG').execute()
    messages = response.data if response.data else []
    
    if not messages:
        print("[WARNING] No messages with status='SUG' found!")
        print("They may already be approved (APR) or scheduled (SCH)")
        return
    
    print(f"Found {len(messages)} messages with status='SUG'")
    print()
    
    # Show sample
    print("Sample messages:")
    for msg in messages[:5]:
        name = msg.get('customer_name', 'Unknown')
        phone = msg.get('phone_number', '')
        campaign = msg.get('campaign_name', 'N/A')
        print(f"  - {name[:25]:25} | {phone[:15]:15} | {campaign}")
    
    if len(messages) > 5:
        print(f"  ... and {len(messages) - 5} more")
    
    print()
    
    if dry_run:
        print("[DRY RUN] Would approve all messages (SUG → APR)")
        print("Run without --dry-run to actually approve")
    else:
        confirm = input(f"Approve all {len(messages)} messages? (type YES): ")
        if confirm != "YES":
            print("Cancelled")
            return
        
        print()
        print("Approving messages...")
        
        try:
            # Bulk update: SUG → APR
            supabase.table('campaign_messages').update({
                'status': 'APR'
            }).eq('status', 'SUG').execute()
            
            print(f"✅ {len(messages)} messages approved!")
            print()
            print("Status changed: SUG → APR")
            print()
            print("Next steps:")
            print("1. Run: schedule_campaign_preview.bat (preview schedule)")
            print("2. Run: schedule_campaign_now.bat (actually schedule)")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("="*70)

if __name__ == "__main__":
    dry_run = '--dry-run' in sys.argv
    approve_all(dry_run=dry_run)

