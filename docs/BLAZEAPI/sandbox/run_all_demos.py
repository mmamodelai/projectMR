#!/usr/bin/env python3
"""
Blaze API Sandbox - Master Demo Script
Runs all sync demos to show Paul our integration
"""

import subprocess
import sys

def run_demo(script_name, description):
    """Run a demo script"""
    print("\n" + "=" * 70)
    print(f"DEMO: {description}")
    print("=" * 70)
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=False,
            text=True
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error running {script_name}: {e}")
        return False

def main():
    print("=" * 70)
    print("BLAZE API SANDBOX - FULL DEMONSTRATION")
    print("=" * 70)
    print("\nThis demo shows:")
    print("1. Customer sync with incremental updates")
    print("2. Transaction sync with date range filtering")
    print("3. Product sync with modified date tracking")
    print("\nAll following Blaze API rules:")
    print("- Incremental sync using modified dates")
    print("- Proper pagination")
    print("- Respecting rate limits")
    print("- Hourly/nightly sync schedules")
    
    # Run all demos
    demos = [
        ("sync_customers.py", "Customer Sync Demo"),
        ("sync_transactions.py", "Transaction Sync Demo"),
        ("sync_products.py", "Product Sync Demo"),
        ("test_rate_limits.py", "Rate Limit Test"),
        ("test_pagination.py", "Pagination Test"),
        ("test_error_handling.py", "Error Handling Test"),
        ("test_endpoints.py", "Endpoint Discovery"),
    ]
    
    results = []
    for script, description in demos:
        success = run_demo(script, description)
        results.append((description, success))
    
    # Summary
    print("\n" + "=" * 70)
    print("DEMONSTRATION SUMMARY")
    print("=" * 70)
    
    for description, success in results:
        status = "SUCCESS" if success else "FAILED"
        print(f"{description}: {status}")
    
    print("\n" + "=" * 70)
    print("Ready to show Paul!")
    print("=" * 70)

if __name__ == "__main__":
    main()
