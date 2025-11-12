#!/usr/bin/env python3
"""
Test phone number normalization
"""

def normalize_phone_number(phone):
    """
    Normalize phone number to E.164 format (+1XXXXXXXXXX)
    """
    if not phone or not isinstance(phone, str):
        return phone
    
    # Remove all non-digit characters
    digits = ''.join(filter(str.isdigit, phone))
    
    # If it starts with 1 and has 11 digits, add +
    if len(digits) == 11 and digits[0] == '1':
        return '+' + digits
    
    # If it has 10 digits, assume US number, add +1
    if len(digits) == 10:
        return '+1' + digits
    
    # If it already has +, return as-is
    if phone.startswith('+'):
        return phone
    
    # Otherwise return original (might be international or invalid)
    return phone

# Test cases
test_numbers = [
    ("619-977-3020", "+16199773020"),
    ("(619) 977-3020", "+16199773020"),
    ("6199773020", "+16199773020"),
    ("16199773020", "+16199773020"),  # 11 digits starting with 1 -> +16199773020
    ("1-619-977-3020", "+16199773020"),
    ("+16199773020", "+16199773020"),
    ("+44 20 7946 0958", "+44 20 7946 0958"),  # International, keep as-is
    ("", ""),
    (None, None),
]

print("=" * 80)
print("PHONE NUMBER NORMALIZATION TESTS")
print("=" * 80)

all_pass = True
for input_phone, expected in test_numbers:
    result = normalize_phone_number(input_phone)
    status = "PASS" if result == expected else "FAIL"
    if result != expected:
        all_pass = False
    
    print(f"\n[{status}]")
    print(f"  Input:    {repr(input_phone)}")
    print(f"  Expected: {expected}")
    print(f"  Got:      {result}")

print("\n" + "=" * 80)
if all_pass:
    print("ALL TESTS PASSED!")
else:
    print("SOME TESTS FAILED - Check above")
print("=" * 80)

