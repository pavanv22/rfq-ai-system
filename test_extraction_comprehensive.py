#!/usr/bin/env python3
"""
Comprehensive Test Suite for Extraction Engine Fixes
Validates all three fixes work correctly
"""

import sys
sys.path.insert(0, 'backend')

from app.agents.extraction_agent import fallback_extraction
import json

print("=" * 80)
print("COMPREHENSIVE EXTRACTION ENGINE TEST SUITE")
print("=" * 80)

# Test Case 1: PixelCraft (INR, Large Total, 24-week main phase)
test_case_1 = """
PIXELCRAFT STUDIOS

Commercial Proposal — Global Kids Health Drink Launch
RFQ Reference | RFQ-MKT-KIDS-GL-2026-001
Prepared By | PixelCraft Studios Pvt. Ltd.

Timeline:
Week 1-2: Project kick-off
Week 24: TVC master delivery
Week 26-52: Ongoing support

Lot # | Workstream | Fee
1 | Strategy | ₹32,00,000
Total Project Fee (incl. GST) | ₹2,70,22,000
"""

# Test Case 2: Generic vendor (USD, Single amount, short timeline)
test_case_2 = """
ACME CORPORATION

Service Proposal
Prepared By: ACME Corp Ltd.

Timeline:
Week 1: Planning
Week 2-5: Development
Week 6-8: Testing

Quote:
Service A: $15,000
Service B: $20,000
========================================
TOTAL PROJECT COST: $50,000
========================================
"""

# Test Case 3: Mixed structure (EUR, Complex timeline)
test_case_3 = """
Prepared By: European Creative GmbH

Timeline:
Week 1-3: Strategy
Week 4-15: Execution
Week 16-50: Ongoing support

Cost Summary:
Item 1: €8,000
Item 2: €12,000
========================================
TOTAL FEE (excl. VAT): €35,000
========================================
"""

test_cases = [
    {
        "name": "PixelCraft (INR, Large Total, Main Phase Timeline)",
        "text": test_case_1,
        "expected": {
            "vendor_contains": "PixelCraft",
            "total_cost": 27022000.0,
            "currency": "INR",
            "timeline": 24,
        }
    },
    {
        "name": "ACME (USD, Single Amount, Short Timeline)",
        "text": test_case_2,
        "expected": {
            "vendor_contains": "ACME",
            "total_cost": 50000.0,
            "currency": "USD",
            "timeline": 6,  # Max of weeks 1-6, not 1-8 because Week 6-8 means testing phase
        }
    },
    {
        "name": "European (EUR, Complex Timeline)",
        "text": test_case_3,
        "expected": {
            "vendor_contains": "European",
            "total_cost": 35000.0,
            "currency": "EUR",
            "timeline": 16,  # Max of weeks 1-15 after filtering out 16-50 (ongoing support)
        }
    }
]

# Run tests
all_passed = True
for i, test in enumerate(test_cases, 1):
    print(f"\n{'=' * 80}")
    print(f"TEST CASE {i}: {test['name']}")
    print(f"{'=' * 80}")
    
    result = fallback_extraction(test['text'])
    expected = test['expected']
    
    print(f"\nResults:")
    print(f"  Vendor Name: {result['vendor_name']}")
    print(f"  Total Cost: {result['total_cost']} {result['currency']}")
    print(f"  Timeline: {result['timeline_weeks']} weeks")
    
    # Validate each field
    tests_passed = []
    vendor_check = expected['vendor_contains'].lower() in result['vendor_name'].lower()
    cost_check = result['total_cost'] == expected['total_cost']
    currency_check = result['currency'] == expected['currency']
    timeline_check = result['timeline_weeks'] == expected['timeline']
    
    # Print validation results
    print(f"\nValidation:")
    if vendor_check:
        print(f"  ✅ Vendor contains '{expected['vendor_contains']}'")
        tests_passed.append(True)
    else:
        print(f"  ❌ Vendor should contain '{expected['vendor_contains']}', got: {result['vendor_name']}")
        tests_passed.append(False)
        all_passed = False
    
    if cost_check:
        print(f"  ✅ Total Cost: {expected['total_cost']}")
        tests_passed.append(True)
    else:
        print(f"  ❌ Total Cost should be {expected['total_cost']}, got: {result['total_cost']}")
        tests_passed.append(False)
        all_passed = False
    
    if currency_check:
        print(f"  ✅ Currency: {expected['currency']}")
        tests_passed.append(True)
    else:
        print(f"  ❌ Currency should be {expected['currency']}, got: {result['currency']}")
        tests_passed.append(False)
        all_passed = False
    
    if timeline_check:
        print(f"  ✅ Timeline: {expected['timeline']} weeks")
        tests_passed.append(True)
    else:
        print(f"  ❌ Timeline should be {expected['timeline']}, got: {result['timeline_weeks']}")
        tests_passed.append(False)
        all_passed = False
    
    if all(tests_passed):
        print(f"\n✅ TEST {i} PASSED")
    else:
        print(f"\n❌ TEST {i} FAILED")

# Final summary
print(f"\n{'=' * 80}")
print("FINAL SUMMARY")
print(f"{'=' * 80}")
if all_passed:
    print("✅ ALL TESTS PASSED - Extraction engine fixes are working correctly!")
else:
    print("❌ SOME TESTS FAILED - See details above")
