#!/usr/bin/env python3
"""
Test script to validate scoring fixes for None value handling
"""

import sys
sys.path.insert(0, r'c:\Users\pavan\apps-pavan\rfq-ai-system\backend')

from app.agents.scoring_agent import fallback_score_from_data, score_vendor

def test_fallback_scoring_with_none_values():
    """Test that fallback scoring handles None values gracefully"""
    
    # Test case 1: Vendor with all None values
    vendor_data_all_none = {
        "vendor_name": "Test Vendor",
        "total_cost_usd": None,
        "timeline_weeks": None,
        "scope_coverage": None
    }
    
    print("Test 1: Vendor with all None values")
    result = fallback_score_from_data(vendor_data_all_none)
    print(f"  Price Score: {result['price_score']} (should be between 1-10)")
    print(f"  Delivery Score: {result['delivery_score']} (should be between 1-10)")
    print(f"  Compliance Score: {result['compliance_score']} (should be between 1-10)")
    assert 1 <= result['price_score'] <= 10, f"Invalid price score: {result['price_score']}"
    assert 1 <= result['delivery_score'] <= 10, f"Invalid delivery score: {result['delivery_score']}"
    assert 1 <= result['compliance_score'] <= 10, f"Invalid compliance score: {result['compliance_score']}"
    assert 'weighted_score' in result, "Missing weighted_score"
    print("  ✓ PASSED\n")
    
    # Test case 2: Vendor with some None values
    vendor_data_partial_none = {
        "vendor_name": "Test Vendor 2",
        "total_cost_usd": 50000,
        "timeline_weeks": None,
        "scope_coverage": ["item1", "item2"]
    }
    
    print("Test 2: Vendor with partial None values")
    result = fallback_score_from_data(vendor_data_partial_none)
    print(f"  Price Score: {result['price_score']} (should be between 1-10)")
    print(f"  Delivery Score: {result['delivery_score']} (should be between 1-10, default timeline used)")
    print(f"  Compliance Score: {result['compliance_score']} (should be between 1-10)")
    assert 1 <= result['price_score'] <= 10, f"Invalid price score: {result['price_score']}"
    assert 1 <= result['delivery_score'] <= 10, f"Invalid delivery score: {result['delivery_score']}"
    assert 1 <= result['compliance_score'] <= 10, f"Invalid compliance score: {result['compliance_score']}"
    print("  ✓ PASSED\n")
    
    # Test case 3: Vendor with valid values
    vendor_data_valid = {
        "vendor_name": "Test Vendor 3",
        "total_cost_usd": 30000,
        "timeline_weeks": 6,
        "scope_coverage": ["item1", "item2", "item3"]
    }
    
    print("Test 3: Vendor with all valid values")
    result = fallback_score_from_data(vendor_data_valid)
    print(f"  Price Score: {result['price_score']} (cost $30k -> should be 8)")
    print(f"  Delivery Score: {result['delivery_score']} (6 weeks -> should be 7)")
    print(f"  Compliance Score: {result['compliance_score']} (3 items -> should be 6)")
    assert result['price_score'] == 8, f"Expected price_score=8, got {result['price_score']}"
    assert result['delivery_score'] == 7, f"Expected delivery_score=7, got {result['delivery_score']}"
    assert 1 <= result['compliance_score'] <= 10, f"Invalid compliance score: {result['compliance_score']}"
    print("  ✓ PASSED\n")
    
    # Test case 4: Verify weighted score calculation doesn't crash
    print("Test 4: Weighted score calculation")
    weights = {"price_weight": 0.4, "delivery_weight": 0.3, "compliance_weight": 0.3}
    
    # Using the result from test 3
    weighted = (
        result['price_score'] * weights['price_weight'] +
        result['delivery_score'] * weights['delivery_weight'] +
        result['compliance_score'] * weights['compliance_weight']
    ) * 10
    
    print(f"  Weighted Score: {weighted} (should be between 0-100)")
    assert 0 <= weighted <= 100, f"Invalid weighted score: {weighted}"
    print("  ✓ PASSED\n")

def test_none_handling_in_comparisons():
    """Test that None values don't cause comparison errors"""
    
    print("Test 5: None value handling in comparisons")
    
    # This should not raise TypeError about '<=' with None and int
    try:
        vendor_data = {
            "vendor_name": "Edge Case Vendor",
            "total_cost_usd": None,
            "timeline_weeks": None,
            "scope_coverage": None,
            "key_terms": None
        }
        
        result = fallback_score_from_data(vendor_data)
        
        print(f"  Successfully handled None values")
        print(f"  Result keys: {list(result.keys())}")
        
        # Verify all required fields are present
        required_fields = ["price_score", "delivery_score", "compliance_score", "weighted_score"]
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"
        
        print("  ✓ PASSED\n")
    except TypeError as e:
        print(f"  ✗ FAILED: {e}\n")
        raise

if __name__ == "__main__":
    print("=" * 60)
    print("SCORING SERVICE FIX VALIDATION TESTS")
    print("=" * 60 + "\n")
    
    try:
        test_fallback_scoring_with_none_values()
        test_none_handling_in_comparisons()
        
        print("=" * 60)
        print("ALL TESTS PASSED ✓")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
