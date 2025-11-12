#!/usr/bin/env python3
"""
Test REAL AI SMS generation with REAL customer data and purchase history
"""

import sys
sys.path.insert(0, '.')

from conductor_integration import ConductorIntegration
from ai_sms_generator import AISMSGenerator

def main():
    print("\n" + "="*70)
    print("TESTING REAL AI SMS GENERATION WITH REAL DATA")
    print("="*70)
    
    # Initialize
    conductor = ConductorIntegration()
    ai_gen = AISMSGenerator()
    
    # Get a real customer
    print("\n1. Loading real customer from Supabase...")
    customers = conductor.get_real_customer_data(limit=1)
    
    if not customers:
        print("   ERROR: No customers found!")
        return
    
    customer = customers[0]
    print(f"   Customer: {customer['name']}")
    print(f"   Phone: {customer['phone']}")
    print(f"   Segment: {customer['segment']}")
    print(f"   LTV: ${customer['ltv']:,.2f}")
    print(f"   Total Visits: {customer['total_visits']}")
    print(f"   Visits/Month: {customer['visits_per_month']}")
    print(f"   Days Since Last Visit: {customer['last_visit_days']}")
    
    # Get purchase history
    print("\n2. Loading REAL purchase history...")
    purchase_history = conductor.get_customer_purchase_history(customer['phone'])
    
    if purchase_history:
        print(f"   Found {len(purchase_history)} unique products!")
        for i, item in enumerate(purchase_history[:5], 1):
            print(f"   {i}. {item['brand']} {item['product_name']} ({item['times_purchased']}x, ${item['total_spent']:.2f})")
    else:
        print("   No purchase history found (will use customer data only)")
    
    # Map customer data for AI
    customer_data_for_ai = {
        'name': customer['name'],
        'segment': customer['segment'],
        'total_visits': customer['total_visits'],
        'days_since_visit': customer['last_visit_days'],
        'ltv': customer['ltv'],
        'favorite_budtender': customer.get('favorite_budtender'),
        'favorite_location': customer.get('favorite_location', 'our dispensary')
    }
    
    # Generate AI SMS
    print("\n3. Generating AI SMS messages...")
    result = ai_gen.generate_sms(customer_data_for_ai, purchase_history, num_options=3)
    
    print(f"\n   Model: {result.get('model')}")
    print(f"   Cost: ${result.get('cost', 0):.6f}")
    print(f"   Tokens: {result.get('tokens_used', 0)}")
    
    print("\n" + "="*70)
    print("GENERATED SMS OPTIONS:")
    print("="*70)
    
    for i, option in enumerate(result['options'], 1):
        print(f"\nOption {i}:")
        print(f"   Tone: {option.get('tone', 'N/A')}")
        print(f"   Message: {option['message']}")
        print(f"   Characters: {len(option['message'])}")
    
    print("\n" + "="*70)
    print("SUCCESS - AI SMS Generation with Real Data Working!")
    print("="*70)

if __name__ == "__main__":
    main()

