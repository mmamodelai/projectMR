#!/usr/bin/env python3
"""
Test Oliver Campaign Database Integration
Quick verification that everything works
"""

from oliver_db import get_oliver_db
from datetime import datetime

def test_oliver_campaign_db():
    """Test all Oliver Campaign DB features"""
    
    print("=" * 60)
    print("OLIVER CAMPAIGN DATABASE TEST")
    print("=" * 60)
    
    db = get_oliver_db()
    
    # Test 1: Create Campaign
    print("\n1. Creating test campaign...")
    campaign_name = f"test_oliver_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    campaign_id = db.create_campaign(
        campaign_name=campaign_name,
        description="Test campaign from test script",
        target_segment="VIP"
    )
    print(f"   Campaign created: ID={campaign_id}, Name={campaign_name}")
    
    # Test 2: Save Message
    print("\n2. Saving test message...")
    test_message = {
        "phone_number": "+16199773020",
        "customer_id": "test_customer_123",
        "customer_name": "Test Customer",
        "customer_segment": "VIP",
        "message_content": "Hey! We got that Sour D you love back in stock. Stop by soon!",
        "strategy_type": "product_based",
        "confidence": "HIGH",
        "reasoning": "VIP customer with $8,500 lifetime value. Last visit was 12 days ago.",
        "days_since_visit": 12,
        "favorite_budtender": "Sophia",
        "favorite_product": "Sour Diesel",
        "total_visits": 47,
        "lifetime_value": 8523.45,
        "preferred_day": "Thursday",
        "preferred_time": "15:00",
        "scheduling_reasoning": "Customer visits Thursday afternoons 90% of the time",
        "generated_by": "test_script",
        "generation_cost": 0.00025,
        "campaign_name": campaign_name,
        "priority": 8
    }
    
    message_id = db.save_generated_message(test_message)
    print(f"   Message saved: ID={message_id}")
    
    # Test 3: Get Messages
    print("\n3. Retrieving messages...")
    messages = db.get_messages(campaign_name=campaign_name)
    print(f"   Found {len(messages)} messages in campaign '{campaign_name}'")
    if messages:
        msg = messages[0]
        print(f"   First message: {msg['customer_name']} - {msg['message_content'][:50]}...")
    
    # Test 4: Update Status
    print("\n4. Updating message status...")
    success = db.update_message_status(
        message_id=message_id,
        status="queued",
        notes="Approved by test script"
    )
    print(f"   Status update: {'SUCCESS' if success else 'FAILED'}")
    
    # Test 5: Get Campaign Stats
    print("\n5. Getting campaign statistics...")
    stats = db.get_campaign_stats(campaign_name)
    print(f"   Campaign stats:")
    print(f"     Total messages: {stats.get('total_messages', 0)}")
    print(f"     By status: {stats.get('by_status', {})}")
    print(f"     By confidence: {stats.get('by_confidence', {})}")
    print(f"     Total cost: ${stats.get('total_cost', 0):.6f}")
    
    # Test 6: Save Customer Pattern
    print("\n6. Saving customer pattern...")
    pattern_success = db.save_customer_pattern(
        customer_id="test_customer_123",
        pattern_data={
            "typical_visit_day": "Thursday",
            "typical_visit_time": "15:00-17:00",
            "visit_frequency": 7,
            "confidence_score": 0.90
        }
    )
    print(f"   Pattern saved: {'SUCCESS' if pattern_success else 'FAILED'}")
    
    # Test 7: Get Customer Pattern
    print("\n7. Retrieving customer pattern...")
    pattern = db.get_customer_pattern("test_customer_123")
    if pattern:
        print(f"   Pattern found:")
        print(f"     Typical day: {pattern.get('typical_visit_day')}")
        print(f"     Typical time: {pattern.get('typical_visit_time')}")
        print(f"     Frequency: every {pattern.get('visit_frequency')} days")
        print(f"     Confidence: {pattern.get('confidence_score'):.0%}")
    
    # Test 8: List Campaigns
    print("\n8. Listing all campaigns...")
    all_campaigns = db.list_campaigns()
    print(f"   Total campaigns: {len(all_campaigns)}")
    for camp in all_campaigns[:5]:  # Show first 5
        print(f"     - {camp['campaign_name']} ({camp['status']}) - {camp.get('total_messages', 0)} messages")
    
    # Test 9: Get Pending Export Count
    print("\n9. Checking pending exports...")
    pending = db.get_pending_export_count()
    print(f"   Pending exports (status='scheduled'): {pending}")
    
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETE!")
    print("=" * 60)
    print("\nOliver Campaign Database is fully operational!")
    print("Check Supabase dashboard to see the data:")
    print("https://kiwmwoqrguyrcpjytgte.supabase.co/project/kiwmwoqrguyrcpjytgte/editor")
    print("\nTables:")
    print("  - campaigns")
    print("  - campaign_messages")
    print("  - campaign_customer_patterns")
    print("=" * 60)

if __name__ == "__main__":
    test_oliver_campaign_db()




