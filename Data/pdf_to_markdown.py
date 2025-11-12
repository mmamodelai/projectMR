#!/usr/bin/env python3
"""
PDF to Markdown Converter
Extracts text from PDF and converts to LLM-friendly markdown format
Part of Conductor SMS System

Usage:
    python pdf_to_markdown.py input.pdf [output.md]
"""

import sys
import re
from pathlib import Path

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF using PyPDF2 or pdfplumber"""
    try:
        import PyPDF2
        return extract_with_pypdf2(pdf_path)
    except ImportError:
        try:
            import pdfplumber
            return extract_with_pdfplumber(pdf_path)
        except ImportError:
            print("ERROR: Need PyPDF2 or pdfplumber. Install with: pip install PyPDF2")
            return None

def extract_with_pypdf2(pdf_path):
    """Extract text using PyPDF2"""
    import PyPDF2
    text_content = []
    
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        
        for page_num, page in enumerate(pdf_reader.pages, 1):
            page_text = page.extract_text()
            if page_text.strip():
                text_content.append(f"## Page {page_num}\n\n{page_text}\n")
    
    return "\n".join(text_content)

def extract_with_pdfplumber(pdf_path):
    """Extract text using pdfplumber (more accurate)"""
    text_content = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            page_text = page.extract_text()
            if page_text and page_text.strip():
                text_content.append(f"## Page {page_num}\n\n{page_text}\n")
    
    return "\n".join(text_content)

def clean_and_structure_text(text):
    """Clean and structure the extracted text for better LLM consumption"""
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    
    # Fix common PDF extraction issues
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)  # Add space between camelCase
    text = re.sub(r'(\w)(\d)', r'\1 \2', text)  # Add space between word and number
    text = re.sub(r'(\d)(\w)', r'\1 \2', text)  # Add space between number and word
    
    # Clean up bullet points and lists
    text = re.sub(r'^[\s]*[•·▪▫]\s*', '- ', text, flags=re.MULTILINE)
    text = re.sub(r'^[\s]*(\d+)[\.\)]\s*', r'\1. ', text, flags=re.MULTILINE)
    
    # Structure headers (look for all caps or title case)
    lines = text.split('\n')
    structured_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            structured_lines.append('')
            continue
            
        # Detect headers (all caps, title case, or numbered sections)
        if (line.isupper() and len(line) > 5 and not line.isdigit()) or \
           (re.match(r'^\d+\.?\s+[A-Z]', line)) or \
           (re.match(r'^[A-Z][a-z]+.*[A-Z][a-z]+', line) and len(line) < 100):
            # Convert to markdown header
            if not line.startswith('#'):
                structured_lines.append(f"\n### {line}\n")
            else:
                structured_lines.append(line)
        else:
            structured_lines.append(line)
    
    return '\n'.join(structured_lines)

def create_structured_markdown(text, title="Retail Budtender Employee Manual"):
    """Create a well-structured markdown document"""
    
    markdown_content = f"""# {title}

*Converted from PDF for LLM consumption*

---

{text}

---

## Document Information
- **Source**: PDF document
- **Conversion Date**: {Path().cwd()}
- **Format**: Markdown for LLM processing
- **Purpose**: Easy text extraction and analysis by AI systems

## Usage Notes
This document has been converted from PDF to markdown format for easier processing by Large Language Models (LLMs). The structure has been preserved as much as possible while making the content more readable and accessible.

"""
    
    return markdown_content

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python pdf_to_markdown.py input.pdf [output.md]")
        sys.exit(1)
    
    pdf_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else pdf_path.with_suffix('.md')
    
    if not pdf_path.exists():
        print(f"ERROR: PDF file not found: {pdf_path}")
        sys.exit(1)
    
    print(f"Extracting text from: {pdf_path}")
    
    # Extract text
    raw_text = extract_text_from_pdf(pdf_path)
    if not raw_text:
        print("ERROR: Failed to extract text from PDF")
        sys.exit(1)
    
    print(f"Extracted {len(raw_text)} characters")
    
    # Clean and structure
    print("Cleaning and structuring text...")
    clean_text = clean_and_structure_text(raw_text)
    
    # Create markdown
    markdown_content = create_structured_markdown(clean_text)
    
    # Write output
    print(f"Writing to: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"[SUCCESS] Conversion complete! Output: {output_path}")
    print(f"[INFO] File size: {len(markdown_content)} characters")

if __name__ == "__main__":
    main()
