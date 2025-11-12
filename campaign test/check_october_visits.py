#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check which at-risk customers actually visited in October
Cross-reference October sales with at-risk customer list
"""

import pandas as pd
import csv
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Read October sales data
print("Reading October sales data...")
october_sales = pd.read_csv('campaign test/October sales.csv')
october_member_ids = set(october_sales['Member ID'].unique())
print(f"Found {len(october_member_ids)} unique customers who purchased in October")

# Read at-risk customer list
print("\nReading at-risk customer list...")
at_risk = pd.read_csv('campaign test/COMPLETE_AT_RISK_CONTACTS_273.csv')
at_risk_ids = set(at_risk['customer_id'].unique())
print(f"Found {len(at_risk_ids)} at-risk customers in our list")

# Find customers who came back in October
came_back = at_risk_ids.intersection(october_member_ids)
print(f"\nGOOD NEWS: {len(came_back)} at-risk customers returned in October!")

# Filter to keep only those who did NOT return
still_at_risk = at_risk[~at_risk['customer_id'].isin(came_back)]
print(f"Still at risk: {len(still_at_risk)} customers")

# Show who came back
if len(came_back) > 0:
    came_back_df = at_risk[at_risk['customer_id'].isin(came_back)][['customer_id', 'name', 'phone', 'tier', 'risk_status', 'lifetime_value', 'last_visit_date']]
    print(f"\nCUSTOMERS WHO RETURNED IN OCTOBER ({len(came_back)}):")
    print("="*100)
    for _, row in came_back_df.iterrows():
        print(f"{row['name']:30} | {row['tier']:10} | {row['risk_status']:10} | LTV: ${row['lifetime_value']:8,.2f} | Last seen: {row['last_visit_date']}")
    
    # Calculate recovered revenue
    recovered_ltv = came_back_df['lifetime_value'].sum()
    print(f"\nRecovered Customer LTV: ${recovered_ltv:,.2f}")

# Save updated list (remove customers who returned)
print(f"\nSaving updated at-risk list...")
still_at_risk.to_csv('campaign test/UPDATED_AT_RISK_CONTACTS.csv', index=False)
print(f"Saved {len(still_at_risk)} customers to UPDATED_AT_RISK_CONTACTS.csv")

# Summary
print("\n" + "="*100)
print("SUMMARY")
print("="*100)
print(f"Original at-risk customers:     {len(at_risk_ids):4}")
print(f"Returned in October:            {len(came_back):4}")
print(f"Still at risk:                  {len(still_at_risk):4}")
print(f"Recovery rate:                  {len(came_back)/len(at_risk_ids)*100:5.1f}%")

