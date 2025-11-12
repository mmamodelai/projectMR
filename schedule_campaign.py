#!/usr/bin/env python3
"""
Campaign Message Scheduler - Random Human-like Timing

Schedules approved campaign messages with:
- Random 4-7 minute intervals between messages
- Random 15-20% skip rate (extra 10-15 min delay to look human)
- Respects business hours (9 AM - 8 PM)

Usage:
    python schedule_campaign.py
"""
from supabase import create_client
from datetime import datetime, timedelta
import random
import sys

# Supabase connection
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Business hours (Pacific Time)
BUSINESS_START = 9  # 9 AM
BUSINESS_END = 20   # 8 PM

def get_next_send_time(current_time, is_first=False):
    """
    Calculate next send time with random human-like delays
    
    - 4-7 minute intervals (random)
    - 15-20% chance of "skip" (extra 10-15 min delay)
    - Respects business hours (9 AM - 8 PM)
    """
    if is_first:
        # First message: start immediately or at next business hour
        if current_time.hour < BUSINESS_START:
            # Before business hours, start at 9 AM
            next_time = current_time.replace(hour=BUSINESS_START, minute=0, second=0, microsecond=0)
        elif current_time.hour >= BUSINESS_END:
            # After hours, start tomorrow at 9 AM
            next_time = current_time + timedelta(days=1)
            next_time = next_time.replace(hour=BUSINESS_START, minute=0, second=0, microsecond=0)
        else:
            # During business hours, start in 1 minute
            next_time = current_time + timedelta(minutes=1)
        return next_time
    
    # Random base interval: 4-7 minutes
    base_delay = random.randint(4, 7)
    
    # 15-20% chance of "human skip" (looks like we got distracted)
    if random.random() < 0.175:  # 17.5% chance
        skip_delay = random.randint(10, 15)
        total_delay = base_delay + skip_delay
        print(f"    [SKIP] Adding extra {skip_delay} min delay (looks human)")
    else:
        total_delay = base_delay
    
    next_time = current_time + timedelta(minutes=total_delay)
    
    # Check if we've gone past business hours
    if next_time.hour >= BUSINESS_END:
        # Resume tomorrow at 9 AM
        next_time = next_time + timedelta(days=1)
        next_time = next_time.replace(hour=BUSINESS_START, minute=0, second=0, microsecond=0)
        print(f"    [PAUSE] Outside business hours, resuming tomorrow at 9 AM")
    
    return next_time

def schedule_campaign_messages(start_time=None, campaign_name=None, dry_run=False):
    """
    Schedule all approved campaign messages that haven't been scheduled yet
    
    Args:
        start_time: When to start (default: now)
        campaign_name: Filter by campaign name (default: all)
        dry_run: If True, show schedule but don't insert (default: False)
    """
    if start_time is None:
        start_time = datetime.now()
    
    print("="*70)
    print("CAMPAIGN SCHEDULER - HUMAN-LIKE RANDOM TIMING")
    print("="*70)
    print(f"Start Time: {start_time.strftime('%Y-%m-%d %I:%M %p')}")
    print(f"Intervals: 4-7 minutes (random)")
    print(f"Human Skips: 15-20% chance of extra 10-15 min delay")
    print(f"Business Hours: {BUSINESS_START} AM - {BUSINESS_END} PM")
    print(f"Dry Run: {'YES (no DB changes)' if dry_run else 'NO (will schedule)'}")
    print("="*70)
    print()
    
    # Get APPROVED campaign messages that haven't been scheduled yet
    # Status: APR (approved, ready to schedule)
    query = supabase.table('campaign_messages').select('*').eq('status', 'APR')
    
    if campaign_name:
        query = query.eq('campaign_name', campaign_name)
    
    response = query.order('id').execute()
    messages = response.data if response.data else []
    
    if not messages:
        print("[WARNING] No approved campaign messages found!")
        print("Make sure campaign_messages have status='APR' (approved)")
        print()
        print("Workflow: SUG (suggested) → APR (approved) → SCH (scheduled)")
        return
    
    print(f"Found {len(messages)} messages to schedule")
    print()
    
    # Check if scheduled_messages table exists, if not skip scheduling logic
    try:
        # Test query to see if table exists
        supabase.table('scheduled_messages').select('id').limit(1).execute()
    except Exception as e:
        print("[WARNING] scheduled_messages table doesn't exist yet")
        print("Will create entries during first scheduling")
    
    # Schedule each message
    current_time = start_time
    scheduled_count = 0
    
    for i, msg in enumerate(messages, 1):
        # Calculate send time
        send_time = get_next_send_time(current_time, is_first=(i == 1))
        
        phone = msg.get('phone_number')
        name = msg.get('customer_name', 'Unknown')
        content = msg.get('message_content', '')
        
        # Count bubbles
        bubbles = content.split('[BUBBLE]')
        bubbles = [b.strip() for b in bubbles if b.strip()]
        bubble_count = len(bubbles) if bubbles else 1
        
        # Display schedule
        delay = int((send_time - current_time).total_seconds() / 60)
        print(f"[{i}/{len(messages)}] {name[:20]:20} | {phone[:15]:15} | "
              f"{send_time.strftime('%m/%d %I:%M %p'):15} | "
              f"+{delay:2}m | {bubble_count} bubbles")
        
        # Insert into scheduled_messages table
        if not dry_run:
            try:
                # Insert into scheduled_messages with status='SCH'
                supabase.table('scheduled_messages').insert({
                    'phone_number': phone,
                    'customer_name': name,
                    'message_content': content,
                    'scheduled_for': send_time.isoformat(),
                    'status': 'SCH',  # SCH = scheduled
                    'campaign_message_id': msg.get('id'),
                    'campaign_name': msg.get('campaign_name'),
                    'created_at': datetime.utcnow().isoformat()
                }).execute()
                
                # Update campaign_messages status: APR → SCH
                supabase.table('campaign_messages').update({
                    'status': 'SCH'
                }).eq('id', msg.get('id')).execute()
                
                scheduled_count += 1
            except Exception as e:
                print(f"    [ERROR] Failed to schedule: {e}")
        
        # Update current time for next iteration
        current_time = send_time
    
    print()
    print("="*70)
    if dry_run:
        print(f"DRY RUN COMPLETE - {len(messages)} messages would be scheduled")
        print("Run without --dry-run to actually schedule")
    else:
        print(f"SCHEDULING COMPLETE: {scheduled_count}/{len(messages)} messages scheduled")
        print()
        print("Next steps:")
        print("1. Supabase pg_cron will auto-process every minute (or Conductor if no pg_cron)")
        print("2. Monitor: SELECT * FROM scheduled_messages WHERE status='SCH'")
        print("3. Cancel anytime: UPDATE scheduled_messages SET status='cancelled' WHERE id=X")
    print("="*70)
    
    # Show summary stats
    if messages:
        first_send = get_next_send_time(start_time, is_first=True)
        last_send = current_time
        duration = (last_send - first_send).total_seconds() / 3600
        print()
        print(f"Campaign Duration: {duration:.1f} hours")
        print(f"First Message: {first_send.strftime('%Y-%m-%d %I:%M %p')}")
        print(f"Last Message: {last_send.strftime('%Y-%m-%d %I:%M %p')}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Schedule campaign messages with human-like timing")
    parser.add_argument('--start', type=str, help='Start time (YYYY-MM-DD HH:MM) - default: now')
    parser.add_argument('--campaign', type=str, help='Filter by campaign name')
    parser.add_argument('--dry-run', action='store_true', help='Show schedule without inserting')
    
    args = parser.parse_args()
    
    # Parse start time
    start_time = None
    if args.start:
        try:
            start_time = datetime.strptime(args.start, '%Y-%m-%d %H:%M')
        except ValueError:
            print(f"[ERROR] Invalid start time format. Use: YYYY-MM-DD HH:MM")
            sys.exit(1)
    
    schedule_campaign_messages(
        start_time=start_time,
        campaign_name=args.campaign,
        dry_run=args.dry_run
    )

if __name__ == "__main__":
    main()

