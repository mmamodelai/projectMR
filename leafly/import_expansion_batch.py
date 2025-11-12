#!/usr/bin/env python3
"""
Batch Import Expansion Leafly Data to Supabase
Generates SQL for 33 strain imports
"""
import json
import os
import sys
import io
from datetime import datetime

# Force UTF-8 encoding for output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("Generating SQL for Leafly Expansion Import...")
print("=" * 70)

# Load expansion Leafly data
leafly_file = os.path.join(os.path.dirname(__file__), '..', 'Data', 'expansion_33_complete.json')
print(f"\nLoading: {leafly_file}")

with open(leafly_file, 'r', encoding='utf-8') as f:
    leafly_data = json.load(f)

print(f"Loaded {len(leafly_data)} strains\n")

# Strain name mappings for fuzzy matching
strain_patterns = {
    "OG Kush": "name ILIKE '%og%kush%' OR name ILIKE '% og %'",
    "Blue Dream": "name ILIKE '%blue%dream%'",
    "Maui Wowie": "name ILIKE '%maui%wowie%' OR name ILIKE '%maui%waui%'",
    "GSC": "name ILIKE '%girl%scout%cookies%' OR name ILIKE '%gsc%'",
    "Sour Diesel": "name ILIKE '%sour%diesel%'",
    "Lemon Haze": "name ILIKE '%lemon%haze%'",
    "Pineapple Express": "name ILIKE '%pineapple%express%'",
    "Wedding Cake": "name ILIKE '%wedding%cake%'",
    "Strawberry Cough": "name ILIKE '%strawberry%cough%'",
    "GG4": "name ILIKE '%gorilla%glue%' OR name ILIKE '%gg4%' OR name ILIKE '%gg #4%'",
    "Mimosa": "name ILIKE '%mimosa%'",
    "Northern Lights": "name ILIKE '%northern%lights%'",
    "Acapulco Gold": "name ILIKE '%acapulco%gold%'",
    "Tangie": "name ILIKE '%tangie%'",
    "Dosidos": "name ILIKE '%do-si-dos%' OR name ILIKE '%dosidos%'",
    "Sherbert": "name ILIKE '%sunset%sherbet%' OR name ILIKE '%sherbert%'",
    "Master Kush": "name ILIKE '%master%kush%'",
    "Cherry Pie": "name ILIKE '%cherry%pie%'",
    "Grape Ape": "name ILIKE '%grape%ape%'",
    "Granddaddy Purple": "name ILIKE '%granddaddy%purple%' OR name ILIKE '%gdp%'",
    "Durban Poison": "name ILIKE '%durban%poison%'",
    "Blueberry": "name ILIKE '%blueberry%' AND (name ILIKE '%og%' OR name ILIKE '%kush%')",
    "Purple Haze": "name ILIKE '%purple%haze%'",
    "Chemdawg": "name ILIKE '%chemdawg%' OR name ILIKE '%chemdog%'",
    "Mango Kush": "name ILIKE '%mango%kush%'",
    "Clementine": "name ILIKE '%clementine%'",
    "Bubba Kush": "name ILIKE '%bubba%kush%'",
    "The Original Z": "name ILIKE '%zkittlez%' OR name ILIKE '%skittlez%'",
    "White Widow": "name ILIKE '%white%widow%'",
    "Trainwreck": "name ILIKE '%trainwreck%'",
    "Skywalker OG": "name ILIKE '%skywalker%og%' OR (name ILIKE '%skywalker%' AND name ILIKE '%og%')",
    "Headband": "name ILIKE '%headband%'",
    "Fire OG": "name ILIKE '%fire%og%'",
}

print("Generating UPDATE statements...\n")

# Generate SQL for each strain
sql_statements = []
strain_count = 0

for strain in leafly_data:
    strain_name = strain['name']
    
    # Get pattern for this strain
    where_pattern = strain_patterns.get(strain_name)
    if not where_pattern:
        print(f"WARNING: No pattern for {strain_name}, using exact match")
        where_pattern = f"name ILIKE '%{strain_name.lower()}%'"
    
    # Build arrays
    effects = "{" + ",".join([f'"{e}"' for e in strain.get('effects', [])]) + "}"
    helps_with = "{" + ",".join([f'"{h}"' for h in strain.get('helps_with', [])]) + "}"
    negatives = "{" + ",".join([f'"{n}"' for n in strain.get('negatives', [])]) + "}"
    flavors = "{" + ",".join([f'"{f}"' for f in strain.get('flavors', [])]) + "}"
    terpenes = "{" + ",".join([f'"{t}"' for t in strain.get('terpenes', [])]) + "}"
    parents = "{" + ",".join([f'"{p}"' for p in strain.get('parent_strains', [])]) + "}"
    
    # Use dollar-quoted strings for description
    description = strain.get('description', '').replace('$$', '')
    lineage = strain.get('lineage', '').replace('$$', '')
    
    sql = f"""
-- Update products for: {strain_name}
UPDATE products
SET
    leafly_strain_type = '{strain.get('strain_type', '')}',
    leafly_description = $${description}$$,
    leafly_rating = {strain.get('rating', 'NULL')},
    leafly_review_count = {strain.get('review_count', 'NULL')},
    effects = '{effects}'::TEXT[],
    helps_with = '{helps_with}'::TEXT[],
    negatives = '{negatives}'::TEXT[],
    flavors = '{flavors}'::TEXT[],
    terpenes = '{terpenes}'::TEXT[],
    parent_strains = '{parents}'::TEXT[],
    lineage = $${lineage}$$,
    image_url = '{strain.get('image_url', '')}',
    leafly_url = '{strain.get('url', '')}',
    leafly_data_updated_at = NOW()
WHERE
    leafly_description IS NULL
    AND ({where_pattern});
"""
    
    sql_statements.append(sql)
    strain_count += 1
    print(f"  [{strain_count:2d}/33] Generated SQL for: {strain_name}")

# Save SQL to file
output_file = os.path.join(os.path.dirname(__file__), 'expansion_import.sql')
with open(output_file, 'w', encoding='utf-8') as f:
    f.write("-- Leafly Expansion Import SQL\n")
    f.write(f"-- Generated: {datetime.now().isoformat()}\n")
    f.write(f"-- Strains: {len(sql_statements)}\n\n")
    f.write("BEGIN;\n\n")
    f.write("\n".join(sql_statements))
    f.write("\n\nCOMMIT;\n")

print(f"\nSQL saved to: {output_file}")
print(f"\nSummary:")
print(f"   - Strains processed: {strain_count}")
print(f"   - SQL statements generated: {len(sql_statements)}")
print(f"\nReady to execute import!")

