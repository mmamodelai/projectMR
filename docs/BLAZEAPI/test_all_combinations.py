#!/usr/bin/env python3
"""
Blaze API - Try ALL Key Combinations
Testing KEY, SECRET, and Partner Key in all possible combinations
"""

import requests

KEY = "48f5dd5e57234145a233c79e66285925"
SECRET = "yuZLWx8b64Q5KyIp03vumIWVhOQ3bxtnpvk5U0i4+9hpHhqL678jmM5RBWCnjfLBMaNZ0//MNG1sM7V9hJqo+Q=="
PARTNER_KEY = "30117b29cdcf44d7a7f4a766e8d398e7"

url = "https://api.partners.blaze.me/api/v1/partner/products"

# Try all 6 combinations
combinations = [
    ('partner_key', PARTNER_KEY, 'Authorization', KEY),
    ('partner_key', PARTNER_KEY, 'Authorization', SECRET),
    ('partner_key', KEY, 'Authorization', PARTNER_KEY),
    ('partner_key', KEY, 'Authorization', SECRET),
    ('partner_key', SECRET, 'Authorization', PARTNER_KEY),
    ('partner_key', SECRET, 'Authorization', KEY),
]

print("=" * 70)
print("TESTING ALL KEY COMBINATIONS")
print("=" * 70)

for i, (key_name, key_val, auth_name, auth_val) in enumerate(combinations, 1):
    print(f"\nCombination {i}:")
    print(f"  {key_name}: {key_val[:20]}...")
    print(f"  {auth_name}: {auth_val[:20]}...")
    
    headers = {
        key_name: key_val,
        auth_name: auth_val,
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers, params={'limit': 1})
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"  SUCCESS! ✅✅✅")
            print(f"  Response: {response.text[:100]}")
            break
        else:
            print(f"  Failed: {response.text[:80]}")
    except Exception as e:
        print(f"  Exception: {e}")

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
