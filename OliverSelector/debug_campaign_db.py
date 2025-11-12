#!/usr/bin/env python3
"""
Debug script to see what's actually in Oliver's Campaign Database
"""

import os
import sys
import json
from typing import List, Dict, Optional

# Add the parent directory to the sys.path to allow imports from the OliverSelector directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from OliverSelector.oliver_db import OliverCampaignDB

def debug_campaign_database():
    """Debug what's actually in Oliver's Campaign Database"""
    print("=== OLIVER CAMPAIGN DATABASE DEBUG ===")
    print()
    
    oliver_db = OliverCampaignDB()
    
    # Get all campaigns
    campaigns = oliver_db.get_all_campaigns()
    print(f"Total campaigns: {len(campaigns)}")
    
    for campaign in campaigns:
        print(f"\nCampaign: {campaign['campaign_name']}")
        print(f"Status: {campaign.get('status', 'unknown')}")
        print(f"Created: {campaign.get('created_at', 'unknown')}")
        
        # Get messages for this campaign
        messages = oliver_db.get_messages_for_campaign(campaign['campaign_name'])
        print(f"Messages in campaign: {len(messages)}")
        
        for i, msg in enumerate(messages):
            print(f"\n  Message {i+1}:")
            print(f"    ID: {msg.get('id', 'N/A')}")
            print(f"    Status: {msg.get('status', 'N/A')}")
            print(f"    Generated: {msg.get('generated_at', 'N/A')}")
            print(f"    Campaign: {msg.get('campaign_name', 'N/A')}")
            
            # Customer data
            customer_data = msg.get('customer_data', {})
            print(f"    Customer Data Keys: {list(customer_data.keys())}")
            print(f"    Customer Name: {customer_data.get('name', 'N/A')}")
            print(f"    Customer Phone: '{customer_data.get('phone', 'N/A')}'")
            print(f"    Customer ID: {customer_data.get('member_id', 'N/A')}")
            
            # Message content
            message_content = msg.get('message_content', '')
            print(f"    Message Preview: {message_content[:100]}...")
            
            # Full message data (first message only)
            if i == 0:
                print(f"\n  FULL MESSAGE DATA:")
                print(json.dumps(msg, indent=2, default=str))

if __name__ == "__main__":
    debug_campaign_database()



