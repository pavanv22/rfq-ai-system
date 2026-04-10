#!/usr/bin/env python3
"""Quick test of extraction services"""
import sys
sys.path.insert(0, '.')

from app.services.extractor import extract_text
from app.agents.extraction_agent import extract_structured_data

# Try to extract from one of our test files
test_file = r"c:\Users\pavan\apps-pavan\rfq-ai-system\test_vendors\vendor_01_techcore.txt"

print("=" * 80)
print("TESTING EXTRACTION PIPELINE")
print("=" * 80)

try:
    print("\n1️⃣ Testing text extraction...")
    text = extract_text(test_file)
    if text:
        print(f"   ✅ Extraction successful! ({len(text)} chars)")
        print(f"   First 300 chars:\n   {text[:300]}\n")
    else:
        print("   ❌ No text extracted\n")
        sys.exit(1)
    
    print("2️⃣ Testing AI structured extraction...")
    structured = extract_structured_data(text)
    if "error" in structured:
        print(f"   ❌ AI extraction failed: {structured['error']}\n")
        sys.exit(1)
    else:
        print(f"   ✅ Structured data extracted!")
        print(f"   Keys: {list(structured.keys())}")
        for key, val in structured.items():
            if key != 'raw_text':
                print(f"   - {key}: {val}")
        print()
    
    print("=" * 80)
    print("✅ ALL TESTS PASSED - Extraction pipeline is working!")
    print("=" * 80)
    
except Exception as e:
    print(f"   ❌ Error: {type(e).__name__}: {str(e)}\n")
    import traceback
    traceback.print_exc()
    sys.exit(1)
