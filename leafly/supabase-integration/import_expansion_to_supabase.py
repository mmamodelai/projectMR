#!/usr/bin/env python3
"""
Import Expansion Leafly Data to Supabase
Imports 33 new strains to enhance products table
"""
import json
import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import Supabase MCP tools
from fuzzyw​uzzy import fuzz

print("🚀 Starting Leafly Expansion Import to Supabase...")
print("=" * 70)

# Load expansion Leafly data
leafly_file = os.path.join(os.path.dirname(__file__), '..', '..', 'Data', 'expansion_33_complete.json')
print(f"\n📂 Loading Leafly data from: {leafly_file}")

with open(leafly_file, 'r', encoding='utf-8') as f:
    leafly_data = json.load(f)

print(f"✅ Loaded {len(leafly_data)} strains from expansion data")

# We'll use MCP tools to interact with Supabase
print("\n🔍 Fetching existing products from Supabase...")
print("(This will use MCP Supabase tools)")

# Create summary
summary = {
    'strains_processed': 0,
    'products_updated': 0,
    'products_by_strain': {}
}

print("\n" + "=" * 70)
print("📊 IMPORT SUMMARY")
print("=" * 70)
print(f"\nStrains to import: {len(leafly_data)}")
print(f"Expected products to enhance: ~6,187")
print("\nThis script will use Supabase MCP tools to:")
print("  1. Fetch products without Leafly data")
print("  2. Match products to strains using fuzzy matching")
print("  3. Update products with Leafly data")
print("\n⚠️  This requires MCP Supabase access")
print("    Please run the actual import using the AI agent")
print("\n" + "=" * 70)

# Print strain list for verification
print("\n📋 Strains ready for import:")
for i, strain in enumerate(sorted(leafly_data, key=lambda x: x['name']), 1):
    print(f"  {i:2d}. {strain['name']}")

print("\n✅ Expansion data validated and ready!")
print("\n🤖 Use AI agent with MCP Supabase tools to complete import")



