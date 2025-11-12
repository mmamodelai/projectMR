#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate Individual Customer Snapshots for Reactivation Campaign
Creates detailed profiles for each at-risk customer
"""

import pandas as pd
import os
from datetime import datetime

# Read the updated at-risk list
print("Reading at-risk customer data...")
at_risk = pd.read_csv('campaign test/UPDATED_AT_RISK_CONTACTS.csv')

# Read October sales to get recent product preferences
october_sales = pd.read_csv('campaign test/October sales.csv')

# Create snapshots directory
os.makedirs('campaign test/customer_snapshots', exist_ok=True)

def generate_snapshot(customer):
    """Generate a detailed snapshot for one customer"""
    
    # Calculate metrics
    days_gone = int(customer['days_since_last_visit'])
    avg_transaction = customer['avg_transaction']
    total_visits = customer['total_visits']
    ltv = customer['lifetime_value']
    
    # Determine urgency level
    if days_gone < 75:
        urgency = "MEDIUM - Cooling Off"
        action = "Light touch, promotional offer"
    elif days_gone < 105:
        urgency = "HIGH - Going Dormant"
        action = "Strong offer, personal message"
    elif days_gone < 135:
        urgency = "URGENT - Nearly Lost"
        action = "Premium offer, call if possible"
    else:
        urgency = "CRITICAL - At Risk of Lost Forever"
        action = "Maximum effort, best offer"
    
    # Calculate visit frequency when active
    if total_visits > 1:
        # Estimate their visit frequency
        visit_frequency = "Weekly" if total_visits > 20 else "Bi-weekly" if total_visits > 10 else "Monthly"
    else:
        visit_frequency = "Unknown"
    
    # Estimate annual value if reactivated
    annual_value = avg_transaction * (52 if visit_frequency == "Weekly" else 26 if visit_frequency == "Bi-weekly" else 12)
    
    snapshot = f"""
{'='*80}
CUSTOMER SNAPSHOT - {customer['name'].upper()}
{'='*80}

CONTACT INFORMATION:
  Phone:          {customer['phone']}
  Email:          {customer['email'] if pd.notna(customer['email']) else 'Not provided'}
  Customer ID:    {customer['customer_id']}

TIER & STATUS:
  Tier:           {customer['tier']}
  Risk Status:    {customer['risk_status']}
  Campaign Wave:  Wave {customer['wave']} Priority

ENGAGEMENT METRICS:
  Last Visit:           {customer['last_visit_date']}
  Days Since Last:      {days_gone} days
  Total Visits:         {total_visits}
  Visit Frequency:      {visit_frequency} (when active)
  
VALUE METRICS:
  Lifetime Value:       ${ltv:,.2f}
  Average Transaction:  ${avg_transaction:,.2f}
  Estimated Annual:     ${annual_value:,.2f} (if reactivated)

URGENCY ASSESSMENT:
  Level:          {urgency}
  Recommended:    {action}

REACTIVATION STRATEGY:
"""
    
    # Add tier-specific strategy
    if customer['tier'] == 'Super VIP':
        snapshot += f"""
  Approach:       VIP Treatment
  Offer:          20-30% off + exclusive product access
  Message:        "We miss you! As one of our top customers, we'd love to 
                  welcome you back with a special VIP offer..."
  Channel:        SMS + Email (if available) + Follow-up call
  Budget:         Up to ${avg_transaction * 0.3:.2f} discount value
"""
    elif customer['tier'] == 'VIP':
        snapshot += f"""
  Approach:       Valued Customer
  Offer:          15-20% off + loyalty bonus
  Message:        "It's been a while! We have some new products you'd love..."
  Channel:        SMS + Email (if available)
  Budget:         Up to ${avg_transaction * 0.2:.2f} discount value
"""
    else:  # Regular
        snapshot += f"""
  Approach:       Win-Back Offer
  Offer:          10-15% off on next visit
  Message:        "Come back and see what's new! Special offer just for you..."
  Channel:        SMS
  Budget:         Up to ${avg_transaction * 0.15:.2f} discount value
"""
    
    # Add timing recommendation
    if customer['risk_status'] == 'Cooling':
        timing = "Week 1 - Send immediately"
    elif customer['risk_status'] == 'Dormant':
        timing = "Week 1-2 - High priority"
    elif customer['risk_status'] == 'Inactive':
        timing = "Week 2-3 - Urgent"
    else:  # At Risk
        timing = "Week 1 - CRITICAL, send ASAP"
    
    snapshot += f"""
CAMPAIGN TIMING:
  Send Window:    {timing}
  Best Time:      Afternoon (2-5 PM) based on customer tier
  Follow-up:      {"48 hours if no response" if customer['tier'] in ['Super VIP', 'VIP'] else "None scheduled"}

SUCCESS METRICS:
  Target ROI:     {300 if customer['tier'] == 'Super VIP' else 200}%
  Break-even:     1 visit at ${avg_transaction:.2f}
  Goal:           Restore to {visit_frequency} visits

NOTES:
  - Customer has been gone for {days_gone} days
  - Historical pattern: {total_visits} visits, ${ltv:,.2f} total spent
  - {"HIGH VALUE - Personal follow-up recommended" if ltv > 1000 else "Standard campaign approach"}
  - {"Consider phone call if SMS doesn't convert" if customer['tier'] == 'Super VIP' else "SMS only unless request callback"}

{'='*80}
"""
    
    return snapshot

# Generate snapshots for all customers
print(f"\nGenerating {len(at_risk)} customer snapshots...")

# Create individual files for each customer
for idx, row in at_risk.iterrows():
    snapshot = generate_snapshot(row)
    
    # Clean filename - remove invalid characters
    clean_name = row['name'].replace(' ', '_').replace('/', '_').replace('"', '').replace("'", '').replace('(', '').replace(')', '')
    filename = f"campaign test/customer_snapshots/{row['customer_id'][:12]}_{clean_name}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(snapshot)
    
    if (idx + 1) % 50 == 0:
        print(f"  Generated {idx + 1}/{len(at_risk)} snapshots...")

print(f"\nCompleted! Generated {len(at_risk)} customer snapshots")

# Also create a master summary file
print("\nCreating master summary report...")

summary = f"""
{'='*80}
AT-RISK CUSTOMER REACTIVATION CAMPAIGN
Master Summary Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
{'='*80}

CAMPAIGN OVERVIEW:
  Total Customers:        {len(at_risk)}
  Total At-Risk Value:    ${at_risk['lifetime_value'].sum():,.2f}
  Average Customer Value: ${at_risk['lifetime_value'].mean():,.2f}

BREAKDOWN BY TIER:
"""

for tier in ['Super VIP', 'VIP', 'Regular']:
    tier_df = at_risk[at_risk['tier'] == tier]
    summary += f"  {tier:12}  {len(tier_df):3} customers  ${tier_df['lifetime_value'].sum():10,.2f} total value\n"

summary += f"""
BREAKDOWN BY RISK STATUS:
"""

for status in ['Cooling', 'Dormant', 'Inactive', 'At Risk']:
    status_df = at_risk[at_risk['risk_status'] == status]
    summary += f"  {status:12}  {len(status_df):3} customers  ${status_df['lifetime_value'].sum():10,.2f} total value\n"

summary += f"""
CAMPAIGN WAVES:
"""

for wave in sorted(at_risk['wave'].unique()):
    wave_df = at_risk[at_risk['wave'] == wave]
    summary += f"  Wave {wave}:       {len(wave_df):3} customers  (avg {wave_df['days_since_last_visit'].mean():.0f} days gone)\n"

summary += f"""
TOP 20 PRIORITY CUSTOMERS (Highest LTV):
{'='*80}
"""

top_20 = at_risk.nlargest(20, 'lifetime_value')[['name', 'tier', 'risk_status', 'days_since_last_visit', 'lifetime_value', 'phone']]
for idx, row in top_20.iterrows():
    summary += f"{row['name']:30} | {row['tier']:10} | {row['risk_status']:10} | {int(row['days_since_last_visit']):3}d | ${row['lifetime_value']:8,.2f} | {row['phone']}\n"

summary += f"""
{'='*80}
IMPLEMENTATION CHECKLIST:
{'='*80}

[ ] Week 1: Send Wave 1 (Super VIP Cooling) - {len(at_risk[at_risk['wave']==1])} customers
[ ] Week 2: Send Wave 2 (Super VIP Dormant + VIP Cooling) - {len(at_risk[at_risk['wave']==2])} customers  
[ ] Week 3: Send Wave 3 (All Inactive + Regular Cooling) - {len(at_risk[at_risk['wave']==3])} customers
[ ] Week 4: Send Wave 4 (At Risk - Last chance) - {len(at_risk[at_risk['wave']==4])} customers

BUDGET ALLOCATION:
  Wave 1 (High Value):    ${(at_risk[at_risk['wave']==1]['avg_transaction'] * 0.25).sum():,.2f} (25% discount budget)
  Wave 2 (Med-High):      ${(at_risk[at_risk['wave']==2]['avg_transaction'] * 0.20).sum():,.2f} (20% discount budget)
  Wave 3 (Medium):        ${(at_risk[at_risk['wave']==3]['avg_transaction'] * 0.15).sum():,.2f} (15% discount budget)
  Wave 4 (Last Chance):   ${(at_risk[at_risk['wave']==4]['avg_transaction'] * 0.10).sum():,.2f} (10% discount budget)
  ----------------------------------------
  Total Campaign Budget:  ${((at_risk[at_risk['wave']==1]['avg_transaction'] * 0.25).sum() + 
                             (at_risk[at_risk['wave']==2]['avg_transaction'] * 0.20).sum() +
                             (at_risk[at_risk['wave']==3]['avg_transaction'] * 0.15).sum() +
                             (at_risk[at_risk['wave']==4]['avg_transaction'] * 0.10).sum()):,.2f}

EXPECTED RESULTS (Conservative 20% conversion):
  Customers Reactivated:  {int(len(at_risk) * 0.20)}
  Revenue Recovery:       ${(at_risk['avg_transaction'].mean() * len(at_risk) * 0.20):,.2f} (first visit)
  Annual Value:           ${(at_risk['avg_transaction'].mean() * 12 * len(at_risk) * 0.20):,.2f} (estimated)

{'='*80}
Individual customer snapshots saved to: campaign test/customer_snapshots/
{'='*80}
"""

with open('campaign test/CAMPAIGN_MASTER_SUMMARY.txt', 'w', encoding='utf-8') as f:
    f.write(summary)

print("Master summary saved to: CAMPAIGN_MASTER_SUMMARY.txt")
print("\nAll customer snapshots ready!")
print(f"Location: campaign test/customer_snapshots/ ({len(at_risk)} files)")

