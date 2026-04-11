#!/usr/bin/env python3
"""Quick test of extraction fixes"""

import sys
sys.path.insert(0, 'backend')

from app.agents.extraction_agent import extract_structured_data, fallback_extraction
import json

# Load a vendor response file to test
test_file = "test_vendors/vendor_06_comprehensive_long.txt"

try:
    with open(test_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    print("=" * 80)
    print("TESTING EXTRACTION WITH FIXED CODE")
    print("=" * 80)
    print(f"\nFile: {test_file}")
    print(f"Text length: {len(text)} chars\n")
    
    # Extract using the fallback (since AI will fail)
    result = fallback_extraction(text)
    
    print("\n" + "=" * 80)
    print("EXTRACTION RESULT:")
    print("=" * 80)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 80)
    print("KEY FIELDS:")
    print("=" * 80)
    print(f"Vendor Name: {result.get('vendor_name', 'N/A')}")
    print(f"Total Cost: {result.get('total_cost', 'N/A')} {result.get('currency', '')}")
    print(f"Timeline: {result.get('timeline_weeks', 'N/A')} weeks")
    print(f"Scope Coverage: {len(result.get('scope_coverage', []))} items")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
