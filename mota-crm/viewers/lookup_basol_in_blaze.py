#!/usr/bin/env python3
"""
Look up Basol Gungor in Blaze API directly
"""
import sys
sys.path.append('../../blaze-api-sync/src')

import requests

# Blaze API credentials (from working sync scripts)
PARTNER_KEY = "30117b29cdcf44d7a7f4a766e8d398e7"
AUTHORIZATION = "48f5dd5e57234145a233c79e66285925"
BASE_URL = "https://api.partners.blaze.me/api/v1/partner"

headers = {
    'partner_key': PARTNER_KEY,
    'Authorization': AUTHORIZATION,
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

print("=" * 80)
print("LOOKING UP BASOL GUNGOR IN BLAZE API")
print("=" * 80)

# Basol's details
member_id = "685d86cde2dd4760bd13c14d"
phone = "(619) 368-3370"
name = "Basol Gungor"

# Method 1: Look up by member ID
print(f"\n1. Looking up by Member ID: {member_id}")
print("-" * 80)

try:
    response = requests.get(
        f"{BASE_URL}/members/{member_id}",
        headers=headers,
        timeout=30
    )
    
    if response.status_code == 200:
        member_data = response.json()
        print(f"\n>>> FOUND in Blaze!")
        print(f"    Name: {member_data.get('firstName')} {member_data.get('lastName')}")
        print(f"    Phone: {member_data.get('mobileNumber')}")
        print(f"    Email: {member_data.get('email', 'N/A')}")
        print(f"    Member Since: {member_data.get('createdDate', 'N/A')[:10]}")
        print(f"    Points Balance: {member_data.get('pointsBalance', 0)}")
        
        # Get his transactions from Blaze
        print(f"\n2. Getting transactions from Blaze for {member_id}")
        print("-" * 80)
        
        try:
            # Try getting transactions with his ID
            tx_response = requests.get(
                f"{BASE_URL}/transactions",
                headers=headers,
                params={
                    'memberId': member_id,
                    'limit': 100
                },
                timeout=30
            )
            
            if tx_response.status_code == 200:
                tx_data = tx_response.json()
                
                # DEBUG: Print raw response
                import json
                print(f"\n>>> RAW RESPONSE:")
                print(json.dumps(tx_data, indent=2)[:500])
                
                values = tx_data.get('values', [])
                total_results = tx_data.get('totalResults', 0)
                
                print(f"\n>>> API says {total_results} total results, returned {len(values)} values")
                
                if len(values) > 0 and values[0].get('totalAmount', 0) > 0:
                    print(f"\n    Basol's transactions:")
                    total = 0
                    for tx in values[:10]:
                        date = tx.get('createdDate', 'N/A')
                        if date != 'N/A':
                            date = date[:10]
                        amount = tx.get('totalAmount', 0)
                        status = tx.get('status', 'Unknown')
                        total += amount
                        print(f"      - {date}: ${amount:.2f} ({status})")
                    
                    if len(values) > 10:
                        print(f"      ... and {len(values) - 10} more")
                    
                    print(f"\n    Total from Blaze: ${total:.2f}")
                    print(f"\n    >>> OUR DATABASE SHOWS: 0 transactions, $0.00")
                    print(f"    >>> BLAZE SHOWS: {total_results} transactions, ${total:.2f}")
                    print(f"\n    *** TRANSACTIONS WERE LOST/MISASSIGNED IN OUR DB! ***")
                elif total_results == 0:
                    print(f"\n    >>> Blaze confirms: 0 transactions")
                    print(f"    Basol really never made a purchase")
                    print(f"    He just signed up for loyalty but never bought anything")
                else:
                    print(f"\n    Blaze shows {total_results} results but they're empty/corrupted")
                    print(f"    API might be returning wrong data")
            else:
                print(f"    Error getting transactions: {tx_response.status_code}")
                print(f"    {tx_response.text[:200]}")
        except Exception as e:
            print(f"    Error fetching transactions: {e}")
    else:
        print(f"\n>>> NOT FOUND in Blaze (status {response.status_code})")
        print(f"    {response.text[:200]}")
        
        # Try searching by phone
        print(f"\n3. Searching by phone: {phone}")
        print("-" * 80)
        
        try:
            search_response = requests.get(
                f"{BASE_URL}/members",
                headers=headers,
                params={
                    'mobileNumber': phone.replace('(', '').replace(')', '').replace(' ', '').replace('-', ''),
                    'limit': 10
                },
                timeout=30
            )
            
            if search_response.status_code == 200:
                search_data = search_response.json()
                members = search_data.get('values', [])
                print(f"\n    Found {len(members)} members with phone {phone}:")
                for m in members:
                    print(f"      - {m.get('firstName')} {m.get('lastName')} ({m.get('id')})")
            else:
                print(f"    Search error: {search_response.status_code}")
        except Exception as e:
            print(f"    Search error: {e}")
        
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 80)

