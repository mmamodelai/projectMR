#!/usr/bin/env python3
"""
Parse MOTA FLOWER DESCRIPTIONS - Understanding the REAL format
The data is text blocks pasted into cells, with products separated by:
1. Product name in a cell (often green highlighted)
2. Parent strain names in next row
3. Long description text blocks
4. "EFFECTS" separator
"""

import pandas as pd
import re

def is_product_name(text):
    """Detect if a cell is a product name (short, not a description)"""
    if pd.isna(text) or text == '':
        return False
    text = str(text).strip()
    # Product names are short (not paragraphs), not numbers, not "EFFECTS"
    if text in ['EFFECTS', 'nan', '', 'MOTA FLOWER DESCRIPTIONS', 'STRAIN #1', 'STRAIN #2', 'STRAIN #3']:
        return False
    if text.startswith('STRAIN #'):
        return False
    # Not a long description (no periods indicating sentences, or very short)
    if len(text) > 150:
        return False
    return True

def extract_products_from_sheet(df, sheet_name):
    """Extract products by identifying the pattern"""
    products = []
    i = 0
    
    print(f"  Scanning {len(df)} rows...")
    
    while i < len(df):
        row = df.iloc[i]
        
        # Look through columns for potential product name
        product_name = None
        product_col = None
        
        for col_idx in range(len(row)):
            cell = row[col_idx]
            if is_product_name(cell):
                # Check if this looks like a product start
                # by seeing if next row has strain names or descriptions
                if i + 1 < len(df):
                    next_row = df.iloc[i + 1]
                    # Look for strain names or long text in next row
                    has_content = any(pd.notna(next_row[j]) and str(next_row[j]).strip() 
                                     for j in range(len(next_row)))
                    if has_content:
                        product_name = str(cell).strip()
                        product_col = col_idx
                        break
        
        if product_name and product_col is not None:
            print(f"    Found product: {product_name} (row {i+2})")
            
            # Get strain names from next row(s)
            strains = []
            strain_descs = []
            gpt_desc = ""
            gpt_short = ""
            effects = []
            
            # Look at next 10 rows to gather all data
            for j in range(i + 1, min(i + 15, len(df))):
                check_row = df.iloc[j]
                
                # Check for "EFFECTS" - marks end of product
                if any(str(check_row[k]).strip() == 'EFFECTS' for k in range(len(check_row))):
                    # Get effects from next row
                    if j + 1 < len(df):
                        effects_row = df.iloc[j + 1]
                        for k in range(len(effects_row)):
                            eff = str(effects_row[k]).strip()
                            if eff and eff != 'nan' and len(eff) < 100:
                                effects.append(eff)
                    break
                
                # Collect strain names and descriptions from columns
                for col_idx in range(len(check_row)):
                    cell_value = check_row[col_idx]
                    if pd.notna(cell_value) and str(cell_value).strip():
                        text = str(cell_value).strip()
                        
                        # Skip if it's just metadata
                        if text in ['nan', '', 'EFFECTS']:
                            continue
                        
                        # Short text might be strain name
                        if len(text) < 100 and len(strains) < 3:
                            # Check if it's not already collected
                            if text not in strains and text != product_name:
                                # Only add if it looks like a strain name (not a sentence)
                                if '.' not in text or len(text.split('.')) < 3:
                                    strains.append(text)
                        
                        # Long text is description
                        elif len(text) > 150:
                            # Guess which column: strain desc vs GPT
                            # Usually GPT descriptions are in later columns (G, H)
                            if col_idx >= 6:  # Column G or later
                                if not gpt_desc:
                                    gpt_desc = text
                                elif not gpt_short and len(text) < len(gpt_desc):
                                    gpt_short = text
                            else:
                                strain_descs.append(text)
            
            # Create product record
            product = {
                'product_name': product_name,
                'category': sheet_name,
                'strain_1': strains[0] if len(strains) > 0 else '',
                'strain_2': strains[1] if len(strains) > 1 else '',
                'strain_3': strains[2] if len(strains) > 2 else '',
                'strain_1_description': strain_descs[0] if len(strain_descs) > 0 else '',
                'strain_2_description': strain_descs[1] if len(strain_descs) > 1 else '',
                'gpt_description': gpt_desc,
                'gpt_description_short': gpt_short,
                'effects': ' | '.join(effects)
            }
            
            products.append(product)
            
            # Skip ahead to avoid re-processing
            i += 10
        else:
            i += 1
    
    return pd.DataFrame(products)

# Main
print("="*60)
print("PARSING MOTA DESCRIPTIONS - REAL FORMAT")
print("="*60)

xl = pd.ExcelFile('MOTA FLOWER DESCRIPTIONS Updated Nov 1 2024.xlsx')

all_products = []

for sheet_name in ['Flower', 'Conc', 'Vapes']:
    print(f"\nSheet: {sheet_name}")
    df = pd.read_excel(xl, sheet_name=sheet_name, header=None)
    
    products_df = extract_products_from_sheet(df, sheet_name)
    
    if not products_df.empty:
        print(f"  [OK] Found {len(products_df)} products")
        all_products.append(products_df)
    else:
        print(f"  [WARN] No products found")

# Combine all
if all_products:
    final_df = pd.concat(all_products, ignore_index=True)
    
    # Save combined
    final_df.to_csv('mota_products_MASTER.csv', index=False)
    print(f"\n{'='*60}")
    print(f"SUCCESS! Created mota_products_MASTER.csv")
    print(f"Total products: {len(final_df)}")
    print(f"{'='*60}")
    
    # Show breakdown
    print("\nBreakdown by category:")
    for cat in final_df['category'].unique():
        count = len(final_df[final_df['category'] == cat])
        print(f"  {cat}: {count} products")
else:
    print("\n[ERROR] No products found!")

