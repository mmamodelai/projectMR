#!/usr/bin/env python3
"""
Test SMSConductor API Server
Tests all endpoints for n8n.io integration
"""

import requests
import json
import time
from datetime import datetime

API_BASE = "http://localhost:5001"

def test_health():
    """Test health check endpoint"""
    print("Testing health check...")
    try:
        response = requests.get(f"{API_BASE}/api/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_status():
    """Test status endpoint"""
    print("\nTesting status...")
    try:
        response = requests.get(f"{API_BASE}/api/status")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_unread_messages():
    """Test unread messages endpoint"""
    print("\nTesting unread messages...")
    try:
        response = requests.get(f"{API_BASE}/api/messages/unread")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_send_message():
    """Test send message endpoint"""
    print("\nTesting send message...")
    try:
        data = {
            "phone_number": "+16199773020",
            "message": f"Test message from API at {datetime.now().strftime('%H:%M:%S')}"
        }
        response = requests.post(
            f"{API_BASE}/api/messages/send",
            headers={'Content-Type': 'application/json'},
            json=data
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_recent_messages():
    """Test recent messages endpoint"""
    print("\nTesting recent messages...")
    try:
        response = requests.get(f"{API_BASE}/api/messages/recent?limit=5")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("SMSConductor API Server Test")
    print("=" * 50)
    print(f"Testing API at: {API_BASE}")
    print()
    
    tests = [
        ("Health Check", test_health),
        ("Status", test_status),
        ("Unread Messages", test_unread_messages),
        ("Send Message", test_send_message),
        ("Recent Messages", test_recent_messages)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            print(f"{'✅' if result else '❌'} {test_name}: {'PASS' if result else 'FAIL'}")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name:20} {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! API server is ready for n8n.io integration.")
    else:
        print("⚠️  Some tests failed. Check API server logs.")

if __name__ == "__main__":
    main()
