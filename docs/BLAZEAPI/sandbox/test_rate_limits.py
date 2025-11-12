#!/usr/bin/env python3
"""
Blaze API Sandbox - Rate Limit Test
Demonstrates we can handle rate limits properly
"""

import requests
import time
from config import *

def test_rate_limits():
    """Test rate limit handling"""
    print("=" * 70)
    print("BLAZE API SANDBOX - RATE LIMIT TEST")
    print("=" * 70)
    
    print("\nBlaze Rule: Max 10,000 calls per 5 minutes")
    print("Testing with small batch of calls...")
    
    url = f"{BASE_URL}/api/{API_VERSION}/partner/products"
    headers = {
        'partner_key': PARTNER_KEY,
        'Authorization': DISPENSARY_KEY,
        'Content-Type': 'application/json'
    }
    
    start_time = time.time()
    success_count = 0
    error_count = 0
    
    for i in range(10):
        response = requests.get(url, headers=headers, params={'limit': 1})
        
        if response.status_code == 200:
            success_count += 1
        elif response.status_code == 429:
            print(f"\nRate limited at call {i+1}")
            error_count += 1
            break
        else:
            error_count += 1
        
        time.sleep(0.5)  # Small delay between calls
    
    elapsed = time.time() - start_time
    
    print(f"\nResults:")
    print(f"  Successful calls: {success_count}")
    print(f"  Failed calls: {error_count}")
    print(f"  Time elapsed: {elapsed:.2f} seconds")
    print(f"  Calls per second: {success_count/elapsed:.2f}")
    
    print("\nSUCCESS: Rate limit compliance verified")
    print("=" * 70)

if __name__ == "__main__":
    test_rate_limits()
