#!/usr/bin/env python3
"""Test phone number hash calculation"""

import hashlib

def normalize_phone_number(phone):
    if not phone or not isinstance(phone, str):
        return phone
    digits = ''.join(filter(str.isdigit, phone))
    if len(digits) == 11 and digits[0] == '1':
        return '+' + digits
    if len(digits) == 10:
        return '+1' + digits
    if phone.startswith('+'):
        return phone
    return phone

def calculate_hash(phone, content):
    return hashlib.md5(f"{phone}|{content}".encode('utf-8')).hexdigest()

# Test different formats
test_content = "Hello test"
formats = ['+16199773020', '16199773020', '6199773020', '(619) 977-3020', '619-977-3020']

print("Testing phone number normalization and hashing:\n")
print("Format".ljust(25) + "Normalized".ljust(20) + "Hash")
print("-" * 80)

hashes = {}
for fmt in formats:
    normalized = normalize_phone_number(fmt)
    hash_val = calculate_hash(normalized, test_content)
    print(f"{fmt:25}{normalized:20}{hash_val}")
    
    if normalized not in hashes:
        hashes[normalized] = []
    hashes[normalized].append((fmt, hash_val))

print("\n" + "="*80)
print("ANALYSIS:")
print("="*80)

# Check if all formats produce same hash
unique_hashes = set([h for h_list in hashes.values() for h in h_list[1]])
if len(unique_hashes) == 1:
    print("✅ ALL formats produce the SAME hash - normalization works correctly!")
else:
    print("❌ Different formats produce DIFFERENT hashes!")
    for norm, pairs in hashes.items():
        unique = set([p[1] for p in pairs])
        if len(unique) > 1:
            print(f"  BUG: {norm} has {len(unique)} different hashes!")

print("\n" + "="*80)
print("POTENTIAL ISSUE:")
print("="*80)
print("If messages were stored BEFORE normalization was added,")
print("they might have different phone formats in the database.")
print("This could cause duplicate detection to fail!")
print("\nCheck if old messages have different formats than new ones.")

