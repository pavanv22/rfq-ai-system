#!/usr/bin/env python3
"""
Test complete extraction pipeline end-to-end
"""
import sys
sys.path.insert(0, r'c:\Users\pavan\apps-pavan\rfq-ai-system\backend')

from app.services.extractor import extract_pdf
from app.agents.extraction_agent import extract_structured_data
from app.services.normalizer import normalize
import os

# Create a test PDF file path (you would use the actual PDF)
# For now, we'll simulate the extracted text
test_text = """[Page 1]
COMMERCIAL PROPOSAL
CreativeEdge Communications Pvt. Ltd.
Response to: RFQ-MKT-KIDS-GL-2026-001
Global Launch – New Kids Health Drink
Prepared By: CreativeEdge Communications Pvt. Ltd.
Date: April 10, 2026

[Page 14]
9.2 Consolidated Project Fee Summary
TOTAL PROJECT FEE (incl. GST + OOP estimate) 3,43,37,900 INR
Currency: All amounts quoted in Indian Rupees (INR).

[Page 10]
8. Timelines & Delivery Plan
Kick-off Week 1 (May 5, 2026)
Final Reporting Week 28 (Oct 26, 2026)

[Page 5]
3. Understanding of Scope
Lot 1 Strategy & Creative Development - Full scope coverage
Lot 2 TVC Development - Full scope coverage
Lot 3 TVC Production - Full scope coverage
Lot 4 Social Organic Content - Full scope coverage
Lot 5 Social Paid Media Planning - Full scope coverage
Lot 6 Social Paid Media Buying & Optimization - Full scope coverage
Lot 7 Kids Advertising & Claims Compliance Review - Full scope coverage
Lot 8 Launch Program Management - Full scope coverage
"""

print("="*60)
print("EXTRACTION PIPELINE TEST")
print("="*60)

# Step 1: Test extraction agent
print("\n1. Testing extraction_agent.extract_structured_data...")
structured = extract_structured_data(test_text)
print(f"   ✓ Vendor: {structured.get('vendor_name')}")
print(f"   ✓ Cost: {structured.get('total_cost')} {structured.get('currency')}")
print(f"   ✓ Timeline: {structured.get('timeline_weeks')} weeks")
print(f"   ✓ Scope items: {len(structured.get('scope_coverage', []))}")

# Step 2: Test normalization
print("\n2. Testing normalization...")
normalized = normalize(structured)
print(f"   ✓ Cost (USD): ${normalized.get('total_cost_usd')}")
print(f"   ✓ Normalized status: {normalized.get('extraction_status')}")

# Step 3: Verification
print("\n3. Verification:")
success = True
checks = [
    ("Vendor correct", "CreativeEdge" in structured.get('vendor_name', '')),
    ("Cost is large", structured.get('total_cost', 0) > 1000000),
    ("Currency is INR", structured.get('currency') == 'INR'),
    ("Timeline is 28 weeks", structured.get('timeline_weeks') == 28),
    ("8 scope items", len(structured.get('scope_coverage', [])) == 8),
    ("Normalized USD cost", normalized.get('total_cost_usd', 0) > 0),
]

for check_name, result in checks:
    status = "✓" if result else "✗"
    print(f"   {status} {check_name}")
    if not result:
        success = False

print("\n" + "="*60)
if success:
    print("ALL TESTS PASSED - Extraction is working correctly!")
    print("\nNEXT STEP: Restart the backend server for changes to take effect")
    print("Terminal: Kill uvicorn and restart with:")
    print(f"  cd backend")
    print(f"  python -m uvicorn app.main:app --reload --port 8001")
else:
    print("SOME TESTS FAILED - There may be an issue with extraction")
print("="*60)
