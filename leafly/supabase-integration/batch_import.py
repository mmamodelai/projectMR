#!/usr/bin/env python3
"""
Batch Leafly Import - Generates SQL for all strains
"""

import json
import os

# Load Leafly data
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LEAFLY_JSON_PATH = os.path.join(PROJECT_ROOT, "Data", "inventory_enhanced_v2.json")

with open(LEAFLY_JSON_PATH, 'r', encoding='utf-8') as f:
    leafly_strains = json.load(f)

# Generate SQL for each strain
sql_statements = []

for strain in leafly_strains:
    name = strain['name']
    
    # Skip strains we already processed
    if 'gelato' in name.lower() or 'runtz' in name.lower():
        continue
    
    # Escape special characters for ILIKE pattern
    search_pattern = name.lower().replace(' ', '%')
    
    # Build arrays safely
    effects = str(strain.get('effects', [])).replace('[', 'ARRAY[').replace(']', ']')
    helps_with = str(strain.get('helps_with', [])).replace('[', 'ARRAY[').replace(']', ']')
    negatives = str(strain.get('negatives', [])).replace('[', 'ARRAY[').replace(']', ']')
    flavors = str(strain.get('flavors', [])).replace('[', 'ARRAY[').replace(']', ']')
    terpenes = str(strain.get('terpenes', [])).replace('[', 'ARRAY[').replace(']', ']')
    parents = str(strain.get('parent_strains', [])).replace('[', 'ARRAY[').replace(']', ']')
    
    rating = strain.get('rating')
    rating_sql = f"{float(rating)}" if rating else "NULL"
    
    review_count = strain.get('review_count')
    review_sql = f"{int(review_count)}" if review_count else "NULL"
    
    lineage = strain.get('lineage', '')
    lineage_sql = f"$${lineage}$$" if lineage else "NULL"
    
    sql = f"""
-- {name}
UPDATE products
SET 
    leafly_strain_type = '{strain.get('strain_type', '')}',
    leafly_description = $${strain.get('description', '')}$$,
    leafly_rating = {rating_sql},
    leafly_review_count = {review_sql},
    effects = {effects},
    helps_with = {helps_with},
    negatives = {negatives},
    flavors = {flavors},
    terpenes = {terpenes},
    parent_strains = {parents},
    lineage = {lineage_sql},
    image_url = '{strain.get('image_url', '')}',
    leafly_url = '{strain.get('url', '')}',
    leafly_data_updated_at = NOW()
WHERE name ILIKE '%{search_pattern}%'
AND leafly_description IS NULL;
"""
    sql_statements.append(sql)

# Write to file
output_path = os.path.join(os.path.dirname(__file__), "batch_updates.sql")
with open(output_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(sql_statements))

print(f"✅ Generated SQL for {len(sql_statements)} strains")
print(f"📄 Saved to: {output_path}")



