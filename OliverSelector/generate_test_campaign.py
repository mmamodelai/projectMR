#!/usr/bin/env python3
"""
Generate a small test campaign (5 messages) for demo purposes
"""

from datetime import datetime, timedelta
import random
from campaign_planner import CampaignPlanner
from oliver_db import OliverCampaignDB

def generate_test_campaign():
    """Generate 5 test messages"""
    planner = CampaignPlanner()
    oliver_db = OliverCampaignDB()
    
    print("\nGenerating TEST campaign with 5 messages...")
    print("="*70)
    
    # Get 5 VIP customers
    campaign = planner.create_campaign_list('win_back_vip')
    customers = campaign['customers'][:5]
    
    print(f"Selected {len(customers)} customers:")
    for i, c in enumerate(customers, 1):
        print(f"  {i}. {c['name']} - {c['phone']} - ${c['ltv']:.2f}")
    
    # Create campaign
    campaign_name = f"TEST Win Back VIPs - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    campaign_id = oliver_db.create_campaign(
        campaign_name=campaign_name,
        description="Test campaign with 5 messages",
        target_segment='VIP'
    )
    
    print(f"\nCampaign created: {campaign_name}")
    print(f"Campaign ID: {campaign_id}")
    
    # Generate messages
    print("\nGenerating messages...")
    start_date = datetime.now() + timedelta(days=1)
    
    for i, customer in enumerate(customers):
        # Simple message template
        first_name = customer['name'].split()[0]
        message_text = f"Hey {first_name}! We noticed you haven't stopped by in a while. "
        message_text += f"We miss you! As a valued VIP customer, we'd love to see you again. "
        message_text += f"Stop by this week!\n\nLuis, Mota Rewards Department"
        
        # Schedule time (spread across day)
        hour = 10 + (i * 2)  # 10am, 12pm, 2pm, 4pm, 6pm
        minute = random.randint(0, 59)
        send_time = start_date.replace(hour=hour, minute=minute)
        
        # Save message
        message_data = {
            'phone_number': customer['phone'],
            'message_content': message_text,
            'customer_name': customer['name'],
            'customer_segment': customer['segment'],
            'confidence': 'HIGH',
            'reasoning': 'Test campaign - VIP win-back',
            'priority': 5,
            'lifetime_value': customer['ltv'],
            'total_visits': customer['total_visits'],
            'days_since_visit': customer['last_visit_days'],
            'campaign_name': campaign_name,
            'preferred_day': send_time.strftime('%A'),
            'preferred_time': send_time.strftime('%H:%M'),
            'scheduling_reasoning': 'Spread evenly across business hours'
        }
        
        msg_id = oliver_db.save_generated_message(message_data)
        
        print(f"  [OK] Message {i+1} saved (ID: {msg_id}) - Scheduled for {send_time.strftime('%I:%M %p')}")
    
    print("\n" + "="*70)
    print("TEST CAMPAIGN COMPLETE!")
    print("="*70)
    print(f"Campaign: {campaign_name}")
    print(f"Messages: 5")
    print(f"Status: DRAFT")
    print("\nNow run: python campaign_review_gui.py")
    print("="*70 + "\n")


if __name__ == "__main__":
    generate_test_campaign()

