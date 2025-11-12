#!/usr/bin/env python3
"""
Blaze API Quick Explorer
Interactive script to explore Blaze API endpoints and data structure

Usage:
    python explore_blaze_api.py
"""

import requests
import json
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

# Production API Credentials
PARTNER_KEY = "30117b29cdcf44d7a7f4a766e8d398e7"
AUTHORIZATION_KEY = "48f5dd5e57234145a233c79e66285925"  # Full key from next_steps.md
BASE_URL = "https://api.partners.blaze.me/api/v1"

def get_headers():
    """Get API request headers"""
    return {
        'partner_key': PARTNER_KEY,
        'Authorization': AUTHORIZATION_KEY,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

def explore_members(limit: int = 5, days_back: int = 7):
    """Explore members endpoint"""
    print("\n" + "="*70)
    print("EXPLORING MEMBERS ENDPOINT")
    print("="*70)
    
    # Calculate date range (last N days, max 7 days per API requirement)
    days_back = min(days_back, 7)  # API restriction: max 7 days
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days_back)
    
    start_ms = int(start_date.timestamp() * 1000)
    end_ms = int(end_date.timestamp() * 1000)
    
    url = f"{BASE_URL}/partner/members"
    params = {
        'startDate': start_ms,
        'endDate': end_ms,
        'limit': limit
    }
    
    print(f"\nRequest:")
    print(f"   URL: {url}")
    print(f"   Date Range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print(f"   Limit: {limit}")
    
    try:
        response = requests.get(url, headers=get_headers(), params=params, timeout=30)
        print(f"\nResponse:")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Show response structure
            print(f"\nResponse Structure:")
            print(f"   Top-level keys: {list(data.keys())}")
            
            if 'values' in data:
                members = data['values']
                print(f"\nFound {len(members)} members:")
                
                for i, member in enumerate(members[:3], 1):  # Show first 3
                    print(f"\n   Member {i}:")
                    print(f"      ID: {member.get('id', 'N/A')}")
                    print(f"      Name: {member.get('firstName', '')} {member.get('lastName', '')}")
                    print(f"      Phone: {member.get('primaryPhone', 'N/A')}")
                    print(f"      Email: {member.get('email', 'N/A')}")
                    print(f"      Status: {member.get('status', 'N/A')}")
                    print(f"      Last Visit: {member.get('lastVisitDate', 'N/A')}")
                    print(f"      Keys available: {list(member.keys())[:10]}...")
            
            # Save sample to file
            with open('blaze_api_members_sample.json', 'w') as f:
                json.dump(data, f, indent=2, default=str)
            print(f"\nSample saved to: blaze_api_members_sample.json")
            
        else:
            print(f"   Error: {response.text[:200]}")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")

def explore_transactions(limit: int = 5, days_back: int = 7):
    """Explore transactions endpoint"""
    print("\n" + "="*70)
    print("EXPLORING TRANSACTIONS ENDPOINT")
    print("="*70)
    
    # Calculate date range (MM/dd/yyyy format per API requirement)
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days_back)
    
    start_iso = start_date.strftime('%m/%d/%Y')
    end_iso = end_date.strftime('%m/%d/%Y')
    
    url = f"{BASE_URL}/partner/transactions"
    params = {
        'startDate': start_iso,
        'endDate': end_iso,
        'limit': limit
    }
    
    print(f"\nRequest:")
    print(f"   URL: {url}")
    print(f"   Date Range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print(f"   Limit: {limit}")
    
    try:
        response = requests.get(url, headers=get_headers(), params=params, timeout=30)
        print(f"\nResponse:")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Show response structure
            print(f"\nResponse Structure:")
            print(f"   Top-level keys: {list(data.keys())}")
            
            if 'values' in data:
                transactions = data['values']
                print(f"\nFound {len(transactions)} transactions:")
                
                for i, txn in enumerate(transactions[:3], 1):  # Show first 3
                    print(f"\n   Transaction {i}:")
                    print(f"      ID: {txn.get('id', 'N/A')}")
                    print(f"      Member ID: {txn.get('memberId', 'N/A')}")
                    print(f"      Status: {txn.get('status', 'N/A')}")
                    
                    # Cart details
                    cart = txn.get('cart', {})
                    if cart:
                        print(f"      Total: ${cart.get('total', 0)}")
                        print(f"      Tax: ${cart.get('tax', 0)}")
                        items = cart.get('items', [])
                        print(f"      Items: {len(items)}")
                        if items:
                            print(f"      First Item: {items[0].get('productName', 'N/A')}")
                    
                    print(f"      Keys available: {list(txn.keys())[:10]}...")
            
            # Save sample to file
            with open('blaze_api_transactions_sample.json', 'w') as f:
                json.dump(data, f, indent=2, default=str)
            print(f"\nSample saved to: blaze_api_transactions_sample.json")
            
        else:
            print(f"   Error: {response.text[:200]}")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")

def explore_products(limit: int = 5):
    """Explore products endpoint"""
    print("\n" + "="*70)
    print("EXPLORING PRODUCTS ENDPOINT")
    print("="*70)
    
    url = f"{BASE_URL}/partner/products"
    params = {'limit': limit}
    
    print(f"\nRequest:")
    print(f"   URL: {url}")
    print(f"   Limit: {limit}")
    
    try:
        response = requests.get(url, headers=get_headers(), params=params, timeout=30)
        print(f"\nResponse:")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Show response structure
            print(f"\nResponse Structure:")
            print(f"   Top-level keys: {list(data.keys())}")
            
            if 'values' in data:
                products = data['values']
                print(f"\nFound {len(products)} products:")
                
                for i, product in enumerate(products[:3], 1):  # Show first 3
                    print(f"\n   Product {i}:")
                    print(f"      ID: {product.get('id', 'N/A')}")
                    print(f"      SKU: {product.get('sku', 'N/A')}")
                    print(f"      Name: {product.get('name', 'N/A')}")
                    print(f"      Category: {product.get('categoryId', 'N/A')}")
                    print(f"      Vendor: {product.get('vendorId', 'N/A')}")
                    print(f"      Price: ${product.get('unitPrice', 0)}")
                    print(f"      Active: {product.get('active', 'N/A')}")
                    print(f"      THC: {product.get('thc', 'N/A')}%")
                    print(f"      CBD: {product.get('cbd', 'N/A')}%")
                    print(f"      Keys available: {list(product.keys())[:15]}...")
            
            # Save sample to file
            with open('blaze_api_products_sample.json', 'w') as f:
                json.dump(data, f, indent=2, default=str)
            print(f"\nSample saved to: blaze_api_products_sample.json")
            
        else:
            print(f"   Error: {response.text[:200]}")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")

def main():
    """Main exploration function"""
    print("\n" + "="*70)
    print("BLAZE API QUICK EXPLORER")
    print("="*70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Base URL: {BASE_URL}")
    print(f"Using Production API")
    
    # Explore each endpoint
    try:
        explore_members(limit=5, days_back=7)
        explore_transactions(limit=5, days_back=7)
        explore_products(limit=5)
        
        print("\n" + "="*70)
        print("EXPLORATION COMPLETE")
        print("="*70)
        print("\nSample files created:")
        print("   - blaze_api_members_sample.json")
        print("   - blaze_api_transactions_sample.json")
        print("   - blaze_api_products_sample.json")
        print("\nNext steps:")
        print("   1. Review the sample JSON files")
        print("   2. Map fields to your Supabase schema")
        print("   3. Test pagination with larger limits")
        print("   4. Build sync scripts based on data structure")
        
    except KeyboardInterrupt:
        print("\n\nExploration interrupted by user")
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

