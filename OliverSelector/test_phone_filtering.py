#!/usr/bin/env python3
"""
Test script to verify phone number filtering is working
"""

import os
import sys

# Add the parent directory to the sys.path to allow imports from the OliverSelector directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from OliverSelector.conductor_integration import ConductorIntegration

def test_phone_filtering():
    """Test that phone number filtering is working"""
    print("=== TESTING PHONE NUMBER FILTERING ===")
    print()
    
    conductor = ConductorIntegration()
    
    # Test the is_valid_phone function
    print("Testing is_valid_phone function:")
    test_phones = [
        ("+13236432223", True, "Valid phone"),
        ("+1", False, "Incomplete phone"),
        ("+1234", False, "Incomplete phone"),
        ("(720) 555-1234", True, "Valid formatted phone"),
        ("", False, "Empty phone"),
        (None, False, "None phone"),
    ]
    
    for phone, expected, description in test_phones:
        result = conductor.is_valid_phone(phone)
        status = "PASS" if result == expected else "FAIL"
        print(f"  {status}: '{phone}' -> {result} ({description})")
    
    print()
    
    # Test loading customers (should filter out invalid phones)
    print("Testing customer loading with phone filtering:")
    customers = conductor.get_real_customer_data(limit=5)
    
    print(f"Loaded {len(customers)} customers")
    
    for i, customer in enumerate(customers):
        phone = customer.get('phone', '')
        name = customer.get('name', 'Unknown')
        is_valid = conductor.is_valid_phone(phone)
        status = "VALID" if is_valid else "INVALID"
        print(f"  {i+1}. {name}: '{phone}' ({status})")
    
    print()
    
    # Check if any invalid phones were loaded
    invalid_phones = [c for c in customers if not conductor.is_valid_phone(c.get('phone', ''))]
    if invalid_phones:
        print(f"ERROR: {len(invalid_phones)} customers with invalid phone numbers were loaded!")
        for customer in invalid_phones:
            print(f"  - {customer.get('name', 'Unknown')}: '{customer.get('phone', '')}'")
    else:
        print("SUCCESS: All loaded customers have valid phone numbers!")

if __name__ == "__main__":
    test_phone_filtering()



