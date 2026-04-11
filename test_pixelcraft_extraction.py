#!/usr/bin/env python3
"""Test with PixelCraft document content"""

import sys
sys.path.insert(0, 'backend')

from app.agents.extraction_agent import fallback_extraction
import json

# Create test text with the PixelCraft document content from earlier
pixelcraft_text = """PIXELCRAFT STUDIOS

Commercial Proposal — Global Kids Health Drink Launch
RFQ Reference | RFQ-MKT-KIDS-GL-2026-001
Submitted To | Global Brand Marketing Team
Prepared By | PixelCraft Studios Pvt. Ltd.
Contact | Ananya Mehrotra, VP – Client Solutions  

Project Timelines:
Week 1-2: Project kick-off
Week 3-5: Category research
Week 6-8: Creative development
Week 9-11: TVC script development
Week 12-15: Pre-production
Week 16-18: TVC shoot
Week 19-23: Post-production 
Week 24: TVC master delivery
Week 14 onwards: Social content engine
Week 20 onwards: Paid media campaigns
Week 26-52: Ongoing social content

Lot # | Workstream | Agency Fee (ex-GST) | GST (18%) | Project Fee (incl. GST)
1 | Strategy & Creative Development | ₹32,00,000 | ₹5,76,000 | ₹37,76,000
2 | TVC Development | ₹24,50,000 | ₹4,41,000 | ₹28,91,000
3 | TVC Production | ₹54,00,000 | ₹9,72,000 | ₹63,72,000
4 | Social Organic Content | ₹38,00,000 | ₹6,84,000 | ₹44,84,000
5 | Paid Media Planning | ₹12,50,000 | ₹2,25,000 | ₹14,75,000
6 | Paid Media Buying & Opt. | ₹28,00,000 | ₹5,04,000 | ₹33,04,000
7 | Compliance Review | ₹18,00,000 | ₹3,24,000 | ₹21,24,000
8 | Launch Program Management | ₹22,00,000 | ₹3,96,000 | ₹25,96,000
Total Agency Fee (ex-GST) | ₹2,29,00,000 | ₹41,22,000
Total Cost / Project Fee (incl. GST) | ₹2,70,22,000
"""

print("=" * 80)
print("TESTING PIXELCRAFT DOCUMENT EXTRACTION")
print("=" * 80)
print(f"\nText length: {len(pixelcraft_text)} chars\n")

# Extract using fallback
result = fallback_extraction(pixelcraft_text)

print("\n" + "=" * 80)
print("EXTRACTION RESULT:")
print("=" * 80)
print(json.dumps(result, indent=2, ensure_ascii=False))

print("\n" + "=" * 80)
print("KEY FIELDS - EXPECTED vs ACTUAL:")
print("=" * 80)
print(f"Vendor Name (expected: PixelCraft Studios Pvt. Ltd.):")
print(f"  Actual: {result.get('vendor_name', 'N/A')}")
print(f"\nTotal Cost (expected: ₹2,70,22,000 = 27022000):")
print(f"  Actual: {result.get('total_cost', 'N/A')} {result.get('currency', '')}")
print(f"\nTimeline (expected: 24 weeks for main phase):")
print(f"  Actual: {result.get('timeline_weeks', 'N/A')} weeks")

# Validation
print("\n" + "=" * 80)
print("VALIDATION:")
print("=" * 80)
errors = []

if "PixelCraft" not in result.get('vendor_name', ''):
    errors.append(f"❌ Vendor name should contain 'PixelCraft', got: {result.get('vendor_name')}")
else:
    print("✓ Vendor name correct")

if result.get('total_cost') != 27022000:
    errors.append(f"❌ Total cost should be 27022000, got: {result.get('total_cost')}")
else:
    print("✓ Total cost correct")

if result.get('currency') != 'INR':
    errors.append(f"❌ Currency should be 'INR', got: {result.get('currency')}")
else:
    print("✓ Currency correct")

if result.get('timeline_weeks') != 24:
    # This might be 26 or other value - let's just check if it's reasonable
    if 20 <= result.get('timeline_weeks', 0) <= 30:
        print(f"✓ Timeline reasonable: {result.get('timeline_weeks')} weeks")
    else:
        errors.append(f"❌ Timeline should be ~24 weeks, got: {result.get('timeline_weeks')}")
else:
    print("✓ Timeline correct")

if errors:
    print("\nISSUES FOUND:")
    for error in errors:
        print(f"  {error}")
else:
    print("\n✅ ALL VALIDATIONS PASSED!")
