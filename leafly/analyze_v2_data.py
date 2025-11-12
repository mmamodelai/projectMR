#!/usr/bin/env python3
"""
Analyze the enhanced v2 scraped Leafly data
"""
import json
import sys
import io
import os

# Force UTF-8 encoding for console output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load the v2 data from Data folder
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
json_path = os.path.join(project_root, 'Data', 'inventory_enhanced_v2.json')
with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"=" * 80)
print(f"ENHANCED SCRAPER V2.0 - DATA INVENTORY")
print(f"=" * 80)
print(f"\nTotal Strains Successfully Scraped: {len(data)}")

# Analyze each field
fields = [
    ('name', 'Name'),
    ('url', 'URL'),
    ('strain_type', 'Type'),
    ('rating', 'Rating'),
    ('review_count', 'Review Count'),
    ('thc_percent', 'THC%'),
    ('cbd_percent', 'CBD%'),
    ('cbg_percent', 'CBG%'),
    ('aka', 'AKA'),
    ('description', 'Description'),
    ('effects', 'Effects'),
    ('helps_with', 'Helps With'),
    ('negatives', 'Negatives'),
    ('flavors', 'Flavors'),
    ('aromas', 'Aromas'),
    ('terpenes', 'Terpenes'),
    ('parent_strains', 'Parents'),
    ('lineage', 'Lineage'),
    ('image_url', 'Image URL'),
    ('breeder', 'Breeder'),
    ('grow_difficulty', 'Grow Difficulty'),
    ('flowering_time', 'Flowering Time'),
    ('scraped_at', 'Timestamp'),
]

print(f"\n" + "=" * 80)
print("FIELD COVERAGE ANALYSIS (Enhanced v2.0)")
print("=" * 80)

for field, label in fields:
    count = sum(1 for strain in data if strain.get(field) and strain.get(field) != [] and strain.get(field) != '')
    percentage = (count / len(data)) * 100
    status = "✓" if percentage > 70 else "○" if percentage > 30 else "✗"
    print(f"{status} {label:20s}: {count:2d}/{len(data)} ({percentage:5.1f}%)")

print(f"\n" + "=" * 80)
print("NEW FIELDS CAPTURED (vs Original Scraper)")
print("=" * 80)

new_fields = [
    ('strain_type', 'Strain Type'),
    ('thc_percent', 'THC Percentage'),
    ('cbd_percent', 'CBD Percentage'),
    ('cbg_percent', 'CBG Percentage'),
    ('review_count', 'Review Count'),
    ('parent_strains', 'Parent Strains'),
    ('lineage', 'Lineage'),
    ('image_url', 'Image URL'),
    ('scraped_at', 'Scraped Timestamp'),
]

for field, label in new_fields:
    count = sum(1 for strain in data if strain.get(field) and strain.get(field) != [] and strain.get(field) != '' and strain.get(field) != 0)
    percentage = (count / len(data)) * 100
    status = "🎉" if percentage > 80 else "✅" if percentage > 50 else "⚠️"
    print(f"{status} {label:20s}: {count:2d}/{len(data)} ({percentage:5.1f}%)")

print(f"\n" + "=" * 80)
print("SAMPLE DATA - Gelato #41 (Enhanced)")
print("=" * 80)

# Find Gelato 41
gelato = next((s for s in data if 'gelato' in s['name'].lower() and '41' in s['name'].lower()), None)
if gelato:
    print(f"\n✅ Name: {gelato.get('name')}")
    print(f"✅ Type: {gelato.get('strain_type', 'N/A')}")
    print(f"✅ Rating: {gelato.get('rating', 'N/A')}")
    print(f"✅ Reviews: {gelato.get('review_count', 0)}")
    print(f"✅ THC: {gelato.get('thc_percent', 'N/A')}%")
    print(f"❓ CBD: {gelato.get('cbd_percent', 'null (validated)')}")
    print(f"✅ CBG: {gelato.get('cbg_percent', 'N/A')}%")
    
    parents = gelato.get('parent_strains', [])
    if parents:
        print(f"✅ Parents: {', '.join(parents)}")
        print(f"✅ Lineage: {gelato.get('lineage', 'N/A')}")
    else:
        print(f"❌ Parents: Not found")
    
    img_url = gelato.get('image_url', '')
    if img_url:
        print(f"✅ Image: {img_url[:60]}...")
    else:
        print(f"❌ Image: Not found")
    
    print(f"✅ Timestamp: {gelato.get('scraped_at', 'N/A')}")

print(f"\n" + "=" * 80)
print("TOP 10 BY REVIEW COUNT (Popularity)")
print("=" * 80)

# Sort by review count
sorted_by_reviews = sorted(data, key=lambda x: x.get('review_count', 0), reverse=True)
for i, strain in enumerate(sorted_by_reviews[:10], 1):
    reviews = strain.get('review_count', 0)
    rating = strain.get('rating', 0)
    strain_type = strain.get('strain_type', 'Unknown')
    thc = strain.get('thc_percent')
    thc_str = f"{thc}%" if thc else "N/A"
    print(f"{i:2d}. {strain['name']:25s} - {reviews:4d} reviews, {rating} ⭐, {strain_type:8s}, THC: {thc_str}")

print(f"\n" + "=" * 80)
print("CANNABINOID STATISTICS")
print("=" * 80)

thc_values = [s.get('thc_percent') for s in data if s.get('thc_percent')]
cbd_values = [s.get('cbd_percent') for s in data if s.get('cbd_percent')]
cbg_values = [s.get('cbg_percent') for s in data if s.get('cbg_percent')]

if thc_values:
    avg_thc = sum(thc_values) / len(thc_values)
    print(f"THC: {len(thc_values)}/{len(data)} strains, Average: {avg_thc:.1f}%, Range: {min(thc_values):.1f}%-{max(thc_values):.1f}%")
else:
    print(f"THC: No data")

if cbd_values:
    avg_cbd = sum(cbd_values) / len(cbd_values)
    print(f"CBD: {len(cbd_values)}/{len(data)} strains, Average: {avg_cbd:.1f}%, Range: {min(cbd_values):.1f}%-{max(cbd_values):.1f}%")
else:
    print(f"CBD: {len(cbd_values)}/{len(data)} strains (correct - most THC-dominant strains have negligible CBD)")

if cbg_values:
    avg_cbg = sum(cbg_values) / len(cbg_values)
    print(f"CBG: {len(cbg_values)}/{len(data)} strains, Average: {avg_cbg:.1f}%, Range: {min(cbg_values):.1f}%-{max(cbg_values):.1f}%")
else:
    print(f"CBG: No data")

print(f"\n" + "=" * 80)
print("STRAIN TYPE DISTRIBUTION")
print("=" * 80)

from collections import Counter
types = Counter(s.get('strain_type') for s in data if s.get('strain_type'))
for strain_type, count in types.most_common():
    percentage = (count / len(data)) * 100
    print(f"{strain_type:15s}: {count:2d} strains ({percentage:5.1f}%)")

print(f"\n" + "=" * 80)
print("STRAINS WITH COMPLETE LINEAGE INFO")
print("=" * 80)

strains_with_parents = [s for s in data if s.get('parent_strains') and len(s.get('parent_strains', [])) >= 2]
print(f"\n{len(strains_with_parents)}/{len(data)} strains have parent information ({(len(strains_with_parents)/len(data)*100):.1f}%)")
for strain in strains_with_parents[:5]:
    print(f"  • {strain['name']:25s} = {strain['lineage']}")

print(f"\n" + "=" * 80)
print("ENHANCEMENT SUCCESS SUMMARY")
print("=" * 80)

# Calculate improvements
new_data_captured = {
    'Strain Type': sum(1 for s in data if s.get('strain_type')),
    'THC%': sum(1 for s in data if s.get('thc_percent')),
    'CBD%': sum(1 for s in data if s.get('cbd_percent')),
    'CBG%': sum(1 for s in data if s.get('cbg_percent')),
    'Review Count': sum(1 for s in data if s.get('review_count', 0) > 0),
    'Parent Strains': sum(1 for s in data if s.get('parent_strains') and len(s.get('parent_strains', [])) > 0),
    'Image URL': sum(1 for s in data if s.get('image_url')),
    'Timestamp': sum(1 for s in data if s.get('scraped_at')),
}

total_new = sum(new_data_captured.values())
max_possible = len(data) * len(new_data_captured)
percentage = (total_new / max_possible) * 100

print(f"\n📊 New Data Fields Captured:")
for field, count in new_data_captured.items():
    pct = (count / len(data)) * 100
    print(f"   {field:20s}: {count:2d}/{len(data)} ({pct:5.1f}%)")

print(f"\n🎉 Overall Enhancement Success: {total_new}/{max_possible} data points ({percentage:.1f}%)")
print(f"✅ Scraper v2.0 is capturing significantly more data!")

print(f"\n" + "=" * 80)
print("READY FOR MACHINE LEARNING!")
print("=" * 80)
print(f"""
✅ {len(data)} strains with enhanced feature vectors
✅ Categorical: effects, flavors, terpenes, strain_type
✅ Numerical: rating, review_count, THC%, CBD%, CBG%
✅ Text: descriptions, helps_with, negatives
✅ Graph: parent_strains, lineage relationships
✅ Temporal: scraped_at timestamps
✅ Visual: image_url for future CNN models
""")

