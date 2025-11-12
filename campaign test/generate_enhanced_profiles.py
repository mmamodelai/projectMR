#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Customer Reporting System
Adds detailed calculations like MoTa CRM v3 info tab
"""

import pandas as pd
import os
from supabase import create_client, Client
from datetime import datetime
import numpy as np

# Supabase connection
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Read at-risk customers
print("Loading at-risk customer list...")
at_risk = pd.read_csv('campaign test/UPDATED_AT_RISK_CONTACTS.csv')
print(f"Found {len(at_risk)} customers to profile")

# Create enhanced profiles directory
os.makedirs('campaign test/enhanced_profiles', exist_ok=True)

def get_comprehensive_profile(customer_id):
    """Get ALL transaction data for comprehensive analysis"""
    
    try:
        # Get all transactions for this customer
        transactions = supabase.table('transactions').select('*').eq('customer_id', customer_id).execute()
        
        if not transactions.data:
            return None, None
        
        # Get all transaction items
        transaction_ids = [t['transaction_id'] for t in transactions.data]
        items = supabase.table('transaction_items').select('*').in_('transaction_id', transaction_ids).execute()
        
        if not items.data:
            return pd.DataFrame(transactions.data), None
        
        return pd.DataFrame(transactions.data), pd.DataFrame(items.data)
        
    except Exception as e:
        print(f"Error getting profile for {customer_id}: {e}")
        return None, None

def calculate_aggregates(transactions_df, items_df):
    """Calculate all the aggregate metrics like MoTa CRM v3 info tab"""
    
    if transactions_df is None or len(transactions_df) == 0:
        return {}
    
    # Transaction-level aggregates
    transaction_amounts = transactions_df['total_amount'].dropna()
    
    aggregates = {
        # Basic transaction metrics
        'total_transactions': len(transactions_df),
        'total_revenue': float(transaction_amounts.sum()) if len(transaction_amounts) > 0 else 0,
        'avg_transaction': float(transaction_amounts.mean()) if len(transaction_amounts) > 0 else 0,
        'min_transaction': float(transaction_amounts.min()) if len(transaction_amounts) > 0 else 0,
        'max_transaction': float(transaction_amounts.max()) if len(transaction_amounts) > 0 else 0,
        'median_transaction': float(transaction_amounts.median()) if len(transaction_amounts) > 0 else 0,
        
        # Visit frequency analysis
        'days_between_visits': [],
        'visit_frequency_score': 0,
        
        # Payment method analysis
        'payment_preferences': {},
        
        # Staff interaction
        'favorite_staff': '',
        'staff_interactions': {},
        
        # Timing patterns
        'visit_times': [],
        'preferred_day_of_week': '',
        'preferred_hour': 0
    }
    
    # Calculate days between visits
    if len(transactions_df) > 1:
        dates = pd.to_datetime(transactions_df['date']).sort_values()
        days_between = dates.diff().dt.days.dropna()
        aggregates['days_between_visits'] = days_between.tolist()
        aggregates['avg_days_between'] = float(days_between.mean()) if len(days_between) > 0 else 0
        
        # Visit frequency score (lower = more frequent)
        aggregates['visit_frequency_score'] = float(days_between.mean()) if len(days_between) > 0 else 999
    
    # Payment method analysis
    if 'payment_type' in transactions_df.columns:
        payment_counts = transactions_df['payment_type'].value_counts()
        aggregates['payment_preferences'] = payment_counts.to_dict()
        aggregates['primary_payment'] = payment_counts.index[0] if len(payment_counts) > 0 else 'Unknown'
    
    # Staff interaction analysis
    if 'staff_name' in transactions_df.columns:
        staff_counts = transactions_df['staff_name'].value_counts()
        aggregates['staff_interactions'] = staff_counts.to_dict()
        aggregates['favorite_staff'] = staff_counts.index[0] if len(staff_counts) > 0 else 'Unknown'
    
    # Timing analysis
    if 'date' in transactions_df.columns:
        dates = pd.to_datetime(transactions_df['date'])
        aggregates['visit_times'] = dates.tolist()
        aggregates['preferred_day_of_week'] = dates.dt.day_name().mode().iloc[0] if len(dates) > 0 else 'Unknown'
        aggregates['preferred_hour'] = int(dates.dt.hour.mode().iloc[0]) if len(dates) > 0 else 12
    
    # Item-level analysis if available
    if items_df is not None and len(items_df) > 0:
        aggregates.update({
            'total_items_purchased': int(items_df['quantity'].sum()),
            'unique_products': len(items_df['product_name'].unique()),
            'avg_items_per_transaction': float(items_df.groupby('transaction_id')['quantity'].sum().mean()),
            'most_purchased_category': items_df['category'].mode().iloc[0] if len(items_df) > 0 else 'Unknown',
            'most_purchased_brand': items_df['brand'].mode().iloc[0] if len(items_df) > 0 else 'Unknown',
            'avg_item_price': float(items_df['unit_price'].mean()) if len(items_df) > 0 else 0,
            'price_range': {
                'min': float(items_df['unit_price'].min()) if len(items_df) > 0 else 0,
                'max': float(items_df['unit_price'].max()) if len(items_df) > 0 else 0
            }
        })
    
    return aggregates

def format_enhanced_profile(customer, aggregates):
    """Format enhanced customer profile with detailed calculations"""
    
    profile = f"""
{'='*100}
ENHANCED CUSTOMER PROFILE - {customer['name'].upper()}
{'='*100}

CONTACT & BASICS:
  Customer ID:    {customer['customer_id']}
  Phone:          {customer['phone']}
  Email:          {customer['email'] if pd.notna(customer['email']) else 'Not provided'}
  Tier:           {customer['tier']}
  Risk Status:    {customer['risk_status']} ({int(customer['days_since_last_visit'])} days gone)

{'='*100}
DETAILED TRANSACTION ANALYSIS (MoTa CRM v3 Style)
{'='*100}

BASIC METRICS:
  Total Transactions:    {aggregates.get('total_transactions', 0):,}
  Total Revenue:         ${aggregates.get('total_revenue', 0):,.2f}
  Average Transaction:   ${aggregates.get('avg_transaction', 0):,.2f}
  Median Transaction:    ${aggregates.get('median_transaction', 0):,.2f}
  Min Transaction:      ${aggregates.get('min_transaction', 0):,.2f}
  Max Transaction:      ${aggregates.get('max_transaction', 0):,.2f}

VISIT PATTERN ANALYSIS:
  Avg Days Between:      {aggregates.get('avg_days_between', 0):.1f} days
  Visit Frequency:       {"Weekly" if aggregates.get('avg_days_between', 0) < 10 else "Bi-weekly" if aggregates.get('avg_days_between', 0) < 20 else "Monthly"}
  Preferred Day:         {aggregates.get('preferred_day_of_week', 'Unknown')}
  Preferred Time:        {aggregates.get('preferred_hour', 12)}:00

PAYMENT & STAFF PREFERENCES:
  Primary Payment:       {aggregates.get('primary_payment', 'Unknown')}
  Favorite Staff:        {aggregates.get('favorite_staff', 'Unknown')}
"""

    # Add payment breakdown if available
    if aggregates.get('payment_preferences'):
        profile += "\n  Payment Method Breakdown:\n"
        for method, count in aggregates['payment_preferences'].items():
            pct = (count / aggregates['total_transactions']) * 100
            profile += f"    {method:15} {count:3} times ({pct:5.1f}%)\n"

    # Add staff breakdown if available
    if aggregates.get('staff_interactions'):
        profile += "\n  Staff Interaction Breakdown:\n"
        for staff, count in list(aggregates['staff_interactions'].items())[:3]:
            pct = (count / aggregates['total_transactions']) * 100
            profile += f"    {staff:20} {count:3} times ({pct:5.1f}%)\n"

    # Add item analysis if available
    if aggregates.get('total_items_purchased'):
        profile += f"""

PRODUCT PURCHASE ANALYSIS:
  Total Items Bought:    {aggregates.get('total_items_purchased', 0):,}
  Unique Products:       {aggregates.get('unique_products', 0):,}
  Avg Items/Visit:       {aggregates.get('avg_items_per_transaction', 0):.1f}
  Favorite Category:     {aggregates.get('most_purchased_category', 'Unknown')}
  Favorite Brand:        {aggregates.get('most_purchased_brand', 'Unknown')}
  Avg Item Price:        ${aggregates.get('avg_item_price', 0):,.2f}
  Price Range:           ${aggregates.get('price_range', {}).get('min', 0):,.2f} - ${aggregates.get('price_range', {}).get('max', 0):,.2f}
"""

    profile += f"""

{'='*100}
REACTIVATION INTELLIGENCE
{'='*100}

CUSTOMER SEGMENTATION:
  Value Tier:            {customer['tier']}
  Engagement Level:      {"High" if aggregates.get('total_transactions', 0) > 20 else "Medium" if aggregates.get('total_transactions', 0) > 10 else "Low"}
  Loyalty Score:         {"High" if aggregates.get('avg_days_between', 999) < 14 else "Medium" if aggregates.get('avg_days_between', 999) < 30 else "Low"}
  Price Sensitivity:     {"Budget" if aggregates.get('avg_transaction', 0) < 30 else "Premium" if aggregates.get('avg_transaction', 0) > 60 else "Moderate"}

PERSONALIZED OFFER STRATEGY:
  Approach:              {"VIP Treatment" if customer['tier'] == 'Super VIP' else "Valued Customer" if customer['tier'] == 'VIP' else "Win-Back Offer"}
  Discount Level:        {"20-30%" if customer['tier'] == 'Super VIP' else "15-20%" if customer['tier'] == 'VIP' else "10-15%"}
  Message Focus:         {aggregates.get('most_purchased_category', 'New Products')} + {aggregates.get('most_purchased_brand', 'Your Favorites')}
  Channel:               {"SMS + Email + Call" if customer['tier'] == 'Super VIP' else "SMS + Email" if customer['tier'] == 'VIP' else "SMS"}
  Timing:                {aggregates.get('preferred_day_of_week', 'Weekday')} around {aggregates.get('preferred_hour', 14)}:00

SUGGESTED MESSAGE:
  "Hi {customer['name'].split()[0]}, we miss you! 🌿
   
   We just restocked {aggregates.get('most_purchased_category', 'your favorites').lower()} from {aggregates.get('most_purchased_brand', 'MOTA')} - 
   your go-to brand! Come back this week and get 20% off.
   
   VIP Code: WELCOME{customer['customer_id'][:6].upper()}
   Valid until {datetime.now().strftime('%m/%d')}"

VALUE RECOVERY PROJECTION:
  Historical Frequency:  {aggregates.get('avg_days_between', 0):.0f} days between visits
  Expected Annual Visits: {int(365 / aggregates.get('avg_days_between', 30)) if aggregates.get('avg_days_between', 0) > 0 else 12}
  Potential Annual Value: ${(aggregates.get('avg_transaction', 0) * int(365 / aggregates.get('avg_days_between', 30))):,.2f}
  
  Campaign ROI Analysis:
  - Discount Budget:     ${aggregates.get('avg_transaction', 0) * 0.20:.2f} (20% off first visit)
  - Break-even:          1 visit
  - 12-month ROI:        {((aggregates.get('avg_transaction', 0) * int(365 / aggregates.get('avg_days_between', 30))) / (aggregates.get('avg_transaction', 0) * 0.20) * 100):.0f}%

{'='*100}
CAMPAIGN EXECUTION PLAN
{'='*100}

Priority Level:          {int(customer['campaign_priority'])}
Wave:                    {int(customer['wave'])}
Send Window:            {"Week 1 - URGENT" if customer['wave'] == 1 else f"Week {int(customer['wave'])}"}
Best Contact Time:      {aggregates.get('preferred_day_of_week', 'Weekday')} at {aggregates.get('preferred_hour', 14)}:00
Follow-up Schedule:     {"48 hours" if customer['tier'] in ['Super VIP', 'VIP'] else "None"}

Success Metrics:
  Target Conversion:     20% (industry standard)
  Expected Revenue:      ${aggregates.get('avg_transaction', 0):,.2f} (first visit)
  Annual Value:          ${(aggregates.get('avg_transaction', 0) * int(365 / aggregates.get('avg_days_between', 30))):,.2f}

NOTES:
  - Customer has been gone for {int(customer['days_since_last_visit'])} days
  - Historical pattern: {aggregates.get('total_transactions', 0)} visits, ${aggregates.get('total_revenue', 0):,.2f} total spent
  - {"HIGH VALUE - Personal follow-up recommended" if aggregates.get('total_revenue', 0) > 1000 else "Standard campaign approach"}
  - {"Consider phone call if SMS doesn't convert" if customer['tier'] == 'Super VIP' else "SMS only unless request callback"}

{'='*100}
"""
    
    return profile

# Process customers
print("\nGenerating enhanced profiles with detailed calculations...")
print("This will take a few minutes as we pull comprehensive data...")

profiles_generated = 0
errors = 0

for idx, row in at_risk.iterrows():
    try:
        # Get comprehensive data
        transactions_df, items_df = get_comprehensive_profile(row['customer_id'])
        
        # Calculate all aggregates
        aggregates = calculate_aggregates(transactions_df, items_df)
        
        # Generate enhanced profile
        profile = format_enhanced_profile(row, aggregates)
        
        # Save to file
        clean_name = row['name'].replace(' ', '_').replace('/', '_').replace('"', '').replace("'", '').replace('(', '').replace(')', '')
        filename = f"campaign test/enhanced_profiles/{row['customer_id'][:12]}_{clean_name}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(profile)
        
        profiles_generated += 1
        
        if (profiles_generated) % 10 == 0:
            print(f"  Generated {profiles_generated}/{len(at_risk)} enhanced profiles...")
        
    except Exception as e:
        errors += 1
        print(f"  ERROR with {row['name']}: {e}")
        continue

print(f"\n{'='*100}")
print(f"ENHANCED PROFILE GENERATION COMPLETE!")
print(f"{'='*100}")
print(f"Successfully Generated:  {profiles_generated}")
print(f"Errors:                  {errors}")
print(f"Output Location:         campaign test/enhanced_profiles/")
print(f"{'='*100}")








