#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deep Profile Analysis for At-Risk Customers
Pulls detailed purchase behavior from Supabase
"""

import pandas as pd
import os
from supabase import create_client, Client
from datetime import datetime

# Supabase connection
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Read at-risk customers
print("Loading at-risk customer list...")
at_risk = pd.read_csv('campaign test/UPDATED_AT_RISK_CONTACTS.csv')
print(f"Found {len(at_risk)} customers to profile")

# Create profiles directory
os.makedirs('campaign test/detailed_profiles', exist_ok=True)

def get_purchase_profile(customer_id):
    """Get detailed purchase behavior from Supabase"""
    
    try:
        # Get all transactions for this customer
        transactions = supabase.table('transactions').select('transaction_id').eq('customer_id', customer_id).execute()
        
        if not transactions.data:
            return None
        
        transaction_ids = [t['transaction_id'] for t in transactions.data]
        
        # Get all transaction items
        items = supabase.table('transaction_items').select('*').in_('transaction_id', transaction_ids).execute()
        
        if not items.data:
            return None
        
        # Convert to dataframe and aggregate
        df = pd.DataFrame(items.data)
        
        # Group by category, flower_type, brand
        grouped = df.groupby(['category', 'flower_type', 'brand'], dropna=False).agg({
            'product_name': 'count',  # times_purchased
            'quantity': 'sum',  # total_quantity
            'total_price': 'sum',  # total_spent
            'unit_price': 'mean'  # avg_price
        }).reset_index()
        
        grouped.columns = ['category', 'flower_type', 'brand', 'times_purchased', 'total_quantity', 'total_spent', 'avg_price']
        grouped = grouped.sort_values('total_spent', ascending=False).head(15)
        
        return grouped
        
    except Exception as e:
        print(f"Error getting profile for {customer_id}: {e}")
        return None

def format_profile(customer, purchase_data):
    """Format rich customer profile"""
    
    profile = f"""
{'='*100}
DETAILED CUSTOMER PROFILE - {customer['name'].upper()}
{'='*100}

CONTACT & BASICS:
  Customer ID:    {customer['customer_id']}
  Phone:          {customer['phone']}
  Email:          {customer['email'] if pd.notna(customer['email']) else 'Not provided'}
  Tier:           {customer['tier']}
  Risk Status:    {customer['risk_status']} ({int(customer['days_since_last_visit'])} days gone)

LIFETIME METRICS:
  Total Visits:         {customer['total_visits']}
  Lifetime Value:       ${customer['lifetime_value']:,.2f}
  Avg Transaction:      ${customer['avg_transaction']:,.2f}
  Last Visit:           {customer['last_visit_date']}

"""
    
    if purchase_data is not None and len(purchase_data) > 0:
        profile += f"""
PURCHASE BEHAVIOR ANALYSIS:
{'='*100}

"""
        
        # Analyze what they buy
        categories = purchase_data.groupby('category')['total_spent'].sum().sort_values(ascending=False)
        
        profile += "PRIMARY PRODUCT CATEGORIES:\n"
        for cat, spent in categories.head(5).items():
            pct = (spent / customer['lifetime_value']) * 100
            profile += f"  {cat:25} ${spent:8,.2f} ({pct:5.1f}% of spend)\n"
        
        # Flower type preference
        if 'flower_type' in purchase_data.columns:
            flower_prefs = purchase_data[purchase_data['flower_type'].notna()].groupby('flower_type')['total_spent'].sum().sort_values(ascending=False)
            if len(flower_prefs) > 0:
                profile += f"\nFLOWER TYPE PREFERENCE:\n"
                for ftype, spent in flower_prefs.head(3).items():
                    profile += f"  {ftype:20} ${spent:8,.2f}\n"
        
        # Brand loyalty
        brands = purchase_data.groupby('brand')['total_spent'].sum().sort_values(ascending=False)
        profile += f"\nTOP BRANDS:\n"
        for brand, spent in brands.head(5).items():
            times = purchase_data[purchase_data['brand'] == brand]['times_purchased'].sum()
            profile += f"  {brand:25} ${spent:8,.2f} ({int(times)} purchases)\n"
        
        # Purchase frequency by category
        profile += f"\nFREQUENT PURCHASES:\n"
        freq_items = purchase_data.nlargest(5, 'times_purchased')[['category', 'brand', 'times_purchased', 'total_spent']]
        for _, item in freq_items.iterrows():
            profile += f"  {item['category']:20} - {item['brand']:20} (bought {int(item['times_purchased'])}x for ${float(item['total_spent']):,.2f})\n"
        
    profile += f"""

{'='*100}
REACTIVATION INTELLIGENCE:
{'='*100}

"""
    
    # Smart recommendations based on their behavior
    if purchase_data is not None and len(purchase_data) > 0:
        top_category = purchase_data.groupby('category')['total_spent'].sum().idxmax()
        top_brand = purchase_data.groupby('brand')['total_spent'].sum().idxmax()
        
        profile += f"""
PERSONALIZED OFFER RECOMMENDATIONS:
  
  Primary Interest:    {top_category}
  Favorite Brand:      {top_brand}
  
  SUGGESTED MESSAGE:
  "Hi {customer['name'].split()[0]}, we miss you! 🌿
   
   We just got fresh {top_category.lower()} from {top_brand} - 
   your favorite! Come back this week and get 20% off.
   
   Your VIP code: WELCOME{customer['customer_id'][:6].upper()}"

  OFFER STRATEGY:
  - Lead with their favorite category ({top_category})
  - Highlight their preferred brand ({top_brand})
  - {"VIP treatment - personal call recommended" if customer['lifetime_value'] > 1000 else "Standard SMS campaign"}
  - Follow-up: {"48 hours" if customer['tier'] in ['Super VIP', 'VIP'] else "None"}

"""
    
    # Calculate potential value
    if customer['total_visits'] > 1:
        visit_freq = "weekly" if customer['total_visits'] > 20 else "bi-weekly" if customer['total_visits'] > 10 else "monthly"
        annual_visits = 52 if visit_freq == "weekly" else 26 if visit_freq == "bi-weekly" else 12
        potential_annual = customer['avg_transaction'] * annual_visits
        
        profile += f"""
VALUE RECOVERY POTENTIAL:
  Historical Frequency:     {visit_freq.capitalize()}
  Expected Annual Visits:   {annual_visits}
  Potential Annual Value:   ${potential_annual:,.2f}
  
  ROI Analysis:
  - Discount Budget:        ${customer['avg_transaction'] * 0.20:.2f} (20% off first visit)
  - Break-even:             1 visit
  - 12-month ROI:           {(potential_annual / (customer['avg_transaction'] * 0.20) * 100):.0f}%

"""
    
    profile += f"""
CAMPAIGN EXECUTION:
  Wave:           {int(customer['wave'])}
  Priority:       {int(customer['campaign_priority'])}
  Send Timing:    {"Week 1 - URGENT" if customer['wave'] == 1 else f"Week {int(customer['wave'])}"}
  Best Time:      Afternoon (2-5 PM)
  Channel:        SMS{"+ Email + Call" if customer['tier'] == 'Super VIP' else " + Email" if customer['tier'] == 'VIP' else ""}

{'='*100}
"""
    
    return profile

# Process customers in batches
print("\nGenerating detailed profiles...")
print("This will take a few minutes as we query Supabase for each customer...")

profiles_generated = 0
errors = 0

for idx, row in at_risk.iterrows():
    try:
        # Get purchase data from Supabase
        purchase_data = get_purchase_profile(row['customer_id'])
        
        # Generate profile
        profile = format_profile(row, purchase_data)
        
        # Save to file
        clean_name = row['name'].replace(' ', '_').replace('/', '_').replace('"', '').replace("'", '').replace('(', '').replace(')', '')
        filename = f"campaign test/detailed_profiles/{row['customer_id'][:12]}_{clean_name}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(profile)
        
        profiles_generated += 1
        
        if (profiles_generated) % 10 == 0:
            print(f"  Generated {profiles_generated}/{len(at_risk)} profiles...")
        
    except Exception as e:
        errors += 1
        print(f"  ERROR with {row['name']}: {e}")
        continue

print(f"\n{'='*100}")
print(f"PROFILE GENERATION COMPLETE!")
print(f"{'='*100}")
print(f"Successfully Generated:  {profiles_generated}")
print(f"Errors:                  {errors}")
print(f"Output Location:         campaign test/detailed_profiles/")
print(f"{'='*100}")

