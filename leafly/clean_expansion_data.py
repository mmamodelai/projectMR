#!/usr/bin/env python3
"""Clean expansion data - remove duplicates"""
import json
import sys

# Read the expansion data
with open('../Data/expansion_33_complete.json', encoding='utf-8') as f:
    data = json.load(f)

print(f"Original count: {len(data)} strains")

# Remove duplicates by name
seen = set()
unique = []
for strain in data:
    if strain['name'] not in seen:
        seen.add(strain['name'])
        unique.append(strain)

print(f"After deduplication: {len(unique)} strains")

# Save cleaned data
with open('../Data/expansion_33_complete.json', 'w', encoding='utf-8') as f:
    json.dump(unique, f, indent=2, ensure_ascii=False)

print("\nFinal strain list (alphabetical):")
for i, strain in enumerate(sorted(unique, key=lambda x: x['name'])):
    print(f"  {i+1:2d}. {strain['name']}")

print(f"\n✓ Saved to Data/expansion_33_complete.json")



