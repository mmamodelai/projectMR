#!/usr/bin/env python3
"""
Markdown to JSON Converter
Converts markdown content to structured JSON for LLM consumption
Part of Conductor SMS System

Usage:
    python markdown_to_json.py input.md [output.json]
"""

import sys
import json
import re
from pathlib import Path

def parse_markdown_to_json(markdown_content):
    """Parse markdown content into structured JSON"""
    
    sections = []
    current_section = None
    current_subsection = None
    current_content = []
    
    lines = markdown_content.split('\n')
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines and metadata
        if not line or line.startswith('*') or line == '---':
            continue
            
        # Page headers
        if line.startswith('## Page '):
            if current_section:
                sections.append(current_section)
            current_section = {
                "type": "page",
                "page_number": int(line.split()[-1]),
                "content": []
            }
            current_subsection = None
            current_content = []
            continue
            
        # Main headers (###)
        if line.startswith('### '):
            # Save previous subsection if exists
            if current_subsection and current_content:
                current_subsection["content"] = '\n'.join(current_content).strip()
                if current_section:
                    current_section["content"].append(current_subsection)
            
            # Start new subsection
            current_subsection = {
                "type": "section",
                "title": line[4:].strip(),
                "content": ""
            }
            current_content = []
            continue
            
        # Regular content
        if line:
            current_content.append(line)
    
    # Add final section
    if current_subsection and current_content:
        current_subsection["content"] = '\n'.join(current_content).strip()
        if current_section:
            current_section["content"].append(current_subsection)
    
    if current_section:
        sections.append(current_section)
    
    return {
        "document_type": "employee_manual",
        "title": "Retail Budtender Employee Manual",
        "company": "MOTA Inc.",
        "version": "March 2022",
        "sections": sections,
        "total_sections": len(sections),
        "metadata": {
            "conversion_date": "2025-01-14",
            "format": "structured_json",
            "purpose": "LLM_consumption"
        }
    }

def extract_key_topics(json_data):
    """Extract key topics and create a summary"""
    topics = []
    
    for section in json_data["sections"]:
        if section["type"] == "page":
            for subsection in section["content"]:
                if subsection["type"] == "section":
                    topic = {
                        "title": subsection["title"],
                        "page": section["page_number"],
                        "summary": subsection["content"][:200] + "..." if len(subsection["content"]) > 200 else subsection["content"]
                    }
                    topics.append(topic)
    
    return topics

def create_llm_optimized_json(markdown_content):
    """Create LLM-optimized JSON structure"""
    
    # Parse to basic JSON
    base_json = parse_markdown_to_json(markdown_content)
    
    # Extract key topics
    topics = extract_key_topics(base_json)
    
    # Create LLM-optimized structure
    llm_json = {
        "document_info": {
            "title": base_json["title"],
            "company": base_json["company"],
            "version": base_json["version"],
            "total_pages": base_json["total_sections"],
            "purpose": "Employee training manual for retail budtenders"
        },
        
        "key_topics": topics,
        
        "detailed_content": base_json["sections"],
        
        "quick_reference": {
            "policies": [t for t in topics if "policy" in t["title"].lower()],
            "procedures": [t for t in topics if any(word in t["title"].lower() for word in ["procedure", "process", "how to"])],
            "requirements": [t for t in topics if "requirement" in t["title"].lower()],
            "safety": [t for t in topics if "safety" in t["title"].lower()]
        },
        
        "conversion_metadata": base_json["metadata"]
    }
    
    return llm_json

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python markdown_to_json.py input.md [output.json]")
        sys.exit(1)
    
    md_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else md_path.with_suffix('.json')
    
    if not md_path.exists():
        print(f"ERROR: Markdown file not found: {md_path}")
        sys.exit(1)
    
    print(f"Converting markdown to JSON: {md_path}")
    
    # Read markdown content
    with open(md_path, 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    print(f"Read {len(markdown_content)} characters from markdown")
    
    # Convert to JSON
    print("Converting to structured JSON...")
    json_data = create_llm_optimized_json(markdown_content)
    
    # Write output
    print(f"Writing to: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    
    print(f"[SUCCESS] Conversion complete! Output: {output_path}")
    print(f"[INFO] JSON structure created with {len(json_data['key_topics'])} topics")
    print(f"[INFO] File size: {len(json.dumps(json_data))} characters")

if __name__ == "__main__":
    main()
