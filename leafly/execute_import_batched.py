#!/usr/bin/env python3
"""
Execute Leafly Expansion Import in Batches
Processes 5 strains at a time for reliability
"""
import re
import sys
import io

# Force UTF-8 encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("Loading SQL file...")
with open('expansion_import.sql', 'r', encoding='utf-8') as f:
    sql_content = f.read()

# Split by strain (each UPDATE statement)
updates = re.split(r'(-- Update products for: .*?\n)', sql_content)

# Reconstruct statements with their headers
strain_updates = []
for i in range(1, len(updates), 2):
    if i+1 < len(updates):
        strain_updates.append(updates[i] + updates[i+1])

print(f"Found {len(strain_updates)} strain UPDATE statements\n")

# Split into batches of 5
batch_size = 5
batches = [strain_updates[i:i+batch_size] for i in range(0, len(strain_updates), batch_size)]

print(f"Split into {len(batches)} batches of {batch_size} strains each\n")

# Save each batch
for idx, batch in enumerate(batches, 1):
    batch_sql = "BEGIN;\n\n" + "\n".join(batch) + "\n\nCOMMIT;"
    
    filename = f"expansion_import_batch{idx}.sql"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(batch_sql)
    
    strain_names = [line.split(': ')[1].strip() for line in "\n".join(batch).split('\n') if line.startswith('-- Update products for:')]
    
    print(f"Batch {idx}: {len(strain_names)} strains")
    for name in strain_names:
        print(f"  - {name}")
    print(f"  Saved to: {filename}\n")

print(f"\nAll batches ready!")
print(f"Execute each batch using MCP Supabase tools")



