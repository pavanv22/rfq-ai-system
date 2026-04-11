#!/usr/bin/env python3
"""
Integration test for scoring service with realistic vendor data
"""

import sys
sys.path.insert(0, r'c:\Users\pavan\apps-pavan\rfq-ai-system\backend')

from app.services.scoring import ScoringService

def test_scoring_integration():
    """Test scoring with realistic vendor data scenarios"""
    
    # Simulate vendors as they would come from database
    vendors = [
        {
            "id": "vendor_1",
            "vendor_name": "TechCore Solutions",
            "total_cost": 50000,
            "currency": "USD",
            "total_cost_usd": 50000,
            "timeline_weeks": 8,
            "scope_coverage": ["module1", "module2", "module3"],
            "key_terms": ["payment in 30 days", "support included"],
            "compliance_score": None
        },
        {
            "id": "vendor_2",
            "vendor_name": "CloudFirst Inc.",
            "total_cost": None,  # Missing cost
            "currency": "USD",
            "total_cost_usd": None,
            "timeline_weeks": None,  # Missing timeline
            "scope_coverage": None,  # Missing scope
            "key_terms": None,
            "compliance_score": None
        },
        {
            "id": "vendor_3",
            "vendor_name": "Global Enterprises",
            "total_cost": 75000,
            "currency": "EUR",
            "total_cost_usd": 82000,
            "timeline_weeks": 12,
            "scope_coverage": ["module1", "module2"],
            "key_terms": ["60 day payment terms"],
            "compliance_score": None
        }
    ]
    
    weights = {
        "price_weight": 0.4,
        "delivery_weight": 0.3,
        "compliance_weight": 0.3
    }
    
    print("Integration Test: Scoring Multiple Vendors")
    print("=" * 60)
    
    try:
        scored_vendors, summary = ScoringService.score_all_vendors(vendors, weights)
        
        print(f"\n✓ Successfully scored {len(scored_vendors)} vendors\n")
        
        # Display results
        for i, vendor in enumerate(scored_vendors, 1):
            scores = vendor.get("scores", {})
            print(f"Vendor {i}: {vendor['vendor_name']}")
            print(f"  Price Score: {scores.get('price_score', 'N/A')}/10")
            print(f"  Delivery Score: {scores.get('delivery_score', 'N/A')}/10")
            print(f"  Compliance Score: {scores.get('compliance_score', 'N/A')}/10")
            print(f"  Weighted Score: {scores.get('weighted_score', 'N/A')}/100")
            print(f"  Status: {'✓ Valid' if all([
                1 <= scores.get('price_score', 0) <= 10,
                1 <= scores.get('delivery_score', 0) <= 10,
                1 <= scores.get('compliance_score', 0) <= 10,
                0 <= scores.get('weighted_score', 0) <= 100
            ]) else '✗ Invalid'}")
            print()
        
        # Display summary
        print(f"Summary:")
        print(f"  Total Vendors: {summary.get('total_vendors')}")
        print(f"  Average Score: {summary.get('average_score')}/100")
        print(f"  Max Score: {summary.get('max_score')}/100")
        print(f"  Min Score: {summary.get('min_score')}/100")
        
        print("\n" + "=" * 60)
        print("✓ INTEGRATION TEST PASSED")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n✗ INTEGRATION TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_scoring_integration()
    sys.exit(0 if success else 1)
