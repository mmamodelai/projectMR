#!/usr/bin/env python3
"""
Test Campaign Message Save
Quick test to verify Oliver Campaign DB is working
"""

from conductor_integration import ConductorIntegration
from datetime import datetime

def test_campaign_save():
    """Test saving a campaign message with REAL customer data"""
    
    print("=" * 60)
    print("TESTING OLIVER CAMPAIGN DATABASE")
    print("=" * 60)
    
    # Initialize integration
    integration = ConductorIntegration()
    
    if not integration.oliver_db:
        print("ERROR: Oliver Campaign DB not initialized!")
        return
    
    print("\n1. Oliver Campaign DB: INITIALIZED")
    
    # Get real customer data
    print("\n2. Fetching real customers from Supabase...")
    customers = integration.get_real_customer_data(limit=1)
    
    if not customers:
        print("ERROR: No customers loaded!")
        return
    
    customer = customers[0]
    print(f"\n   Found customer:")
    print(f"   - Name: {customer.get('name')}")
    print(f"   - Phone: {customer.get('phone')}")
    print(f"   - Segment: {customer.get('segment')}")
    print(f"   - LTV: ${customer.get('ltv', 0):.2f}")
    print(f"   - Total Visits: {customer.get('total_visits', 0)}")
    print(f"   - Last Visit: {customer.get('last_visit_days', 0)} days ago")
    
    # Prepare customer data
    customer_data = {
        "member_id": customer.get('member_id'),
        "name": customer.get('name'),
        "phone": customer.get('phone'),
        "segment": customer.get('segment'),
        "ltv": customer.get('ltv'),
        "total_visits": customer.get('total_visits'),
        "last_visit_days": customer.get('last_visit_days'),
        "favorite_budtender": None,
        "favorite_product": None
    }
    
    # Prepare message data
    message_content = f"Hi {customer.get('name', 'there').split()[0]}! We miss our {customer.get('segment', 'valued')} customer! 30% off + $20 credit today only!"
    
    message_data = {
        "content": message_content,
        "strategy_type": "win_back",
        "confidence": "HIGH" if customer.get('ltv', 0) > 1000 else "MEDIUM",
        "reasoning": f"{customer.get('segment')} customer with ${customer.get('ltv', 0):.2f} LTV. Last visit was {customer.get('last_visit_days', 0)} days ago.",
        "preferred_day": "any",
        "preferred_time": "any",
        "scheduling_reasoning": "Test message from campaign save script",
        "generated_by": "test_campaign_save_script",
        "generation_cost": 0.0,
        "priority": 8
    }
    
    # Save to Campaign DB
    print("\n3. Saving message to Oliver Campaign DB...")
    campaign_name = f"test_script_campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    message_id = integration.save_campaign_message(
        customer_data,
        message_data,
        campaign_name
    )
    
    if message_id:
        print(f"\n   SUCCESS! Message saved with ID: {message_id}")
        print(f"   Campaign: {campaign_name}")
        print(f"   Status: draft")
        print(f"\n   Message Content:")
        print(f"   \"{message_content}\"")
        
        # Verify it's in the database
        print("\n4. Verifying message in database...")
        messages = integration.get_campaign_messages(campaign_name=campaign_name)
        
        if messages:
            msg = messages[0]
            print(f"\n   VERIFIED! Message found in database:")
            print(f"   - ID: {msg.get('id')}")
            print(f"   - Customer: {msg.get('customer_name')}")
            print(f"   - Phone: {msg.get('customer_name')}")
            print(f"   - Status: {msg.get('status')}")
            print(f"   - Priority: {msg.get('priority')}")
            print(f"   - Confidence: {msg.get('confidence')}")
            print(f"   - Strategy: {msg.get('strategy_type')}")
            
            print("\n" + "=" * 60)
            print("SUCCESS! OLIVER CAMPAIGN DATABASE IS WORKING!")
            print("=" * 60)
            print("\nCheck Supabase to see the message:")
            print("https://kiwmwoqrguyrcpjytgte.supabase.co")
            print("Table: campaign_messages")
            print("=" * 60)
        else:
            print("   WARNING: Message not found in database query")
    else:
        print("\n   ERROR: Failed to save message!")

if __name__ == "__main__":
    test_campaign_save()




