#!/usr/bin/env python3
"""Debug extraction from DOCX document"""

import sys
sys.path.insert(0, r'c:\Users\pavan\apps-pavan\rfq-ai-system\backend')

from app.services import extractor
from app.agents.extraction_agent import extract_structured_data
import json
import os
from pathlib import Path

# Find the most recent DOCX file uploaded
uploads_dir = Path(r'c:\Users\pavan\apps-pavan\rfq-ai-system\backend\data\uploads')
docx_files = list(uploads_dir.glob('*.docx'))

if not docx_files:
    print("No DOCX files found")
    sys.exit(1)

# Get most recent
latest_docx = max(docx_files, key=os.path.getctime)
docx_path = str(latest_docx)

print("=" * 80)
print("EXTRACTION DEBUG")
print("=" * 80)
print(f"\nFile: {latest_docx.name}")

# Extract raw text
print("\n[Step 1] Extracting raw text from document...")
raw_text = extractor.extract_text(docx_path)

if not raw_text:
    print("ERROR: No text extracted")
    sys.exit(1)

print(f"Extracted {len(raw_text)} characters\n")
print("--- FULL DOCUMENT TEXT ---")
print(raw_text)
print("--- END DOCUMENT ---\n")

# Try LLM extraction
print("[Step 2] Parsing with extraction agent...")
try:
    result = extract_structured_data(raw_text)
    print("\nExtraction Result:")
    print(json.dumps(result, indent=2))
except Exception as e:
    print(f"Extraction failed: {e}")

"""Debug extraction issues with PixelCraft DOCX"""

import sys
sys.path.insert(0, r'c:\Users\pavan\apps-pavan\rfq-ai-system\backend')

from backend.app.services.extractor import VendorExtractor
import json

# Initialize extractor
extractor = VendorExtractor()

# The file path where it would be uploaded
docx_path = 'backend/data/uploads/Vendor4_PixelCraft_Proposal.docx'

print("=" * 70)
print("EXTRACTION DEBUG: PixelCraft Proposal")
print("=" * 70)

try:
    # Step 1: Extract raw text
    print("\n[Step 1] Extracting raw text from DOCX...")
    raw_text = extractor.extract_text(docx_path, file_type='docx')
    
    print(f"Raw text length: {len(raw_text)} characters")
    print("\n--- RAW TEXT (first 2000 chars) ---")
    print(raw_text[:2000])
    print("\n--- RAW TEXT (last 1000 chars) ---")
    print(raw_text[-1000:])
    
    # Save raw text for inspection
    with open('extracted_raw_text.txt', 'w') as f:
        f.write(raw_text)
    print("\n✓ Raw text saved to 'extracted_raw_text.txt'")
    
    # Step 2: Try extraction with LLM (this is where things might go wrong)
    print("\n[Step 2] Attempting LLM extraction (if Ollama available)...")
    print("(This will show what the LLM extracted)")
    
    try:
        llm_result = extractor._extract_with_llm(raw_text)
        print(f"\nLLM Result:")
        print(json.dumps(llm_result, indent=2))
    except Exception as e:
        print(f"LLM extraction failed: {e}")
        print("Will try regex extraction instead...")
    
    # Step 3: Try regex extraction
    print("\n[Step 3] Attempting regex extraction...")
    regex_result = extractor._extract_with_regex(raw_text)
    print(f"\nRegex Result:")
    print(json.dumps(regex_result, indent=2))
    
    # Step 4: Show what specific fields were found
    print("\n[Step 4] Field Analysis:")
    print(f"  Vendor Name: {regex_result.get('vendor_name', 'NOT FOUND')}")
    print(f"  Total Cost: {regex_result.get('total_cost', 'NOT FOUND')}")
    print(f"  Currency: {regex_result.get('currency', 'NOT FOUND')}")
    print(f"  Timeline: {regex_result.get('timeline_weeks', 'NOT FOUND')}")
    print(f"  Scope Coverage: {regex_result.get('scope_coverage', 'NOT FOUND')}")
    
except FileNotFoundError:
    print(f"\n✗ File not found: {docx_path}")
    print("Make sure the file is uploaded to the backend/data/uploads/ directory")
except Exception as e:
    print(f"\n✗ Error during extraction: {e}")
    import traceback
    traceback.print_exc()
