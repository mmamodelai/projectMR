#!/usr/bin/env python3
"""
Test script for Leafly scraper
Tests the scraper with known strains and validates output
"""

import sys
import json
from leafly_scraper import LeaflyScraper


def test_gelato_41():
    """Test scraping Gelato #41 (known good strain)"""
    print("=" * 60)
    print("TEST 1: Scraping Gelato #41")
    print("=" * 60)
    
    scraper = LeaflyScraper()
    data = scraper.scrape_strain(url="https://www.leafly.com/strains/gelato-41")
    
    if not data:
        print("❌ FAILED: Could not scrape data")
        return False
    
    # Validate required fields
    required_fields = ['name', 'strain_type', 'effects', 'flavors']
    missing = [f for f in required_fields if not data.get(f)]
    
    if missing:
        print(f"❌ FAILED: Missing fields: {missing}")
        return False
    
    # Print results
    print(f"\n✅ SUCCESS: Scraped {data['name']}")
    print(f"   Type: {data['strain_type']}")
    print(f"   THC: {data.get('thc_percent', 'N/A')}%")
    print(f"   Rating: {data.get('rating', 'N/A')}")
    print(f"   Effects: {', '.join(data['effects'][:3])}")
    print(f"   Flavors: {', '.join(data['flavors'][:3])}")
    
    return True


def test_strain_by_name():
    """Test scraping by strain name"""
    print("\n" + "=" * 60)
    print("TEST 2: Scraping by name (Black Cherry Gelato)")
    print("=" * 60)
    
    scraper = LeaflyScraper()
    data = scraper.scrape_strain(strain_name="Black Cherry Gelato")
    
    if not data:
        print("❌ FAILED: Could not scrape data")
        return False
    
    print(f"\n✅ SUCCESS: Scraped {data['name']}")
    print(f"   URL: {data['url']}")
    print(f"   Type: {data['strain_type']}")
    
    return True


def test_batch_scraping():
    """Test batch scraping"""
    print("\n" + "=" * 60)
    print("TEST 3: Batch scraping (3 strains)")
    print("=" * 60)
    
    test_strains = [
        "Gelato 41",
        "Runtz",
        "OG Kush"
    ]
    
    scraper = LeaflyScraper()
    results = scraper.scrape_batch(test_strains)
    
    if len(results) < 2:  # Allow 1 failure
        print(f"❌ FAILED: Only scraped {len(results)}/{len(test_strains)} strains")
        return False
    
    print(f"\n✅ SUCCESS: Scraped {len(results)}/{len(test_strains)} strains")
    for strain in results:
        print(f"   - {strain['name']}")
    
    return True


def test_json_export():
    """Test JSON export"""
    print("\n" + "=" * 60)
    print("TEST 4: JSON export")
    print("=" * 60)
    
    scraper = LeaflyScraper()
    data = scraper.scrape_strain(strain_name="Jack Herer")
    
    if not data:
        print("❌ FAILED: Could not scrape data")
        return False
    
    try:
        scraper.export_to_json([data], "test_output.json")
        
        # Verify file contents
        with open("test_output.json", 'r') as f:
            loaded = json.load(f)
        
        if len(loaded) != 1:
            print("❌ FAILED: JSON export contains wrong number of records")
            return False
        
        print("\n✅ SUCCESS: JSON export working")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def run_all_tests():
    """Run all tests"""
    print("\n" + "🧪" * 30)
    print("LEAFLY SCRAPER TEST SUITE")
    print("🧪" * 30 + "\n")
    
    tests = [
        ("Scrape Gelato #41", test_gelato_41),
        ("Scrape by name", test_strain_by_name),
        ("Batch scraping", test_batch_scraping),
        ("JSON export", test_json_export),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ ERROR in {name}: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())

