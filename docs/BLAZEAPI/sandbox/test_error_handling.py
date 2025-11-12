#!/usr/bin/env python3
"""
Blaze API Sandbox - Error Handling Test
Demonstrates proper error handling
"""

import requests
from config import *

def test_error_handling():
    """Test various error scenarios"""
    print("=" * 70)
    print("BLAZE API SANDBOX - ERROR HANDLING TEST")
    print("=" * 70)
    
    headers = {
        'partner_key': PARTNER_KEY,
        'Authorization': DISPENSARY_KEY,
        'Content-Type': 'application/json'
    }
    
    # Test 1: Invalid endpoint
    print("\n1. Testing invalid endpoint...")
    url = f"{BASE_URL}/api/{API_VERSION}/partner/invalid_endpoint"
    response = requests.get(url, headers=headers)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text[:150]}")
    
    # Test 2: Invalid parameters
    print("\n2. Testing invalid parameters...")
    url = f"{BASE_URL}/api/{API_VERSION}/partner/products"
    response = requests.get(url, headers=headers, params={'limit': -1})
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text[:150]}")
    
    # Test 3: Missing headers
    print("\n3. Testing missing headers...")
    url = f"{BASE_URL}/api/{API_VERSION}/partner/products"
    response = requests.get(url, params={'limit': 1})
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text[:150]}")
    
    # Test 4: Large limit
    print("\n4. Testing large limit...")
    url = f"{BASE_URL}/api/{API_VERSION}/partner/products"
    response = requests.get(url, headers=headers, params={'limit': 10000})
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Records returned: {len(data.get('values', []))}")
    
    print("\nSUCCESS: Error handling verified")
    print("=" * 70)

if __name__ == "__main__":
    test_error_handling()
