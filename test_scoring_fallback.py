#!/usr/bin/env python3
"""
Test the complete scoring pipeline without calling Ollama
(Bypasses LLM by using fallback directly via ScoringService)
"""

import sys
sys.path.insert(0, r'c:\Users\pavan\apps-pavan\rfq-ai-system\backend')

# Monkey-patch to skip Ollama calls
import openai
def mock_create(*args, **kwargs):
    raise Exception("Forced to use fallback (Ollama not running)")
openai.ChatCompletion.create = mock_create

from app.services.scoring import ScoringService

def test_scoring_with_fallback_only():
    """Test scoring pipeline with Ollama unavailable (forces fallback)"""
    
    vendors = [
        {
            "id": "vendor_1",
            "vendor_name": "TechCore",
            "total_cost_usd": 50000,
            "timeline_weeks": 8,
            "scope_coverage": ["feature1", "feature2", "feature3"],
            "key_terms": ["30-day payment"],
            "compliance_score": None
        },
        {
            "id": "vendor_2",
            "vendor_name": "CloudFirst (Missing Data)",
            "total_cost_usd": None,
            "timeline_weeks": None,
            "scope_coverage": None,
            "key_terms": None,
            "compliance_score": None
        },
        {
            "id": "vendor_3",
            "vendor_name": "Enterprise Solutions",
            "total_cost_usd": 120000,
            "timeline_weeks": 4,
            "scope_coverage": ["feature1", "feature2"],
            "key_terms": ["60-day payment", "premium support"],
            "compliance_score": None
        }
    ]
    
    weights = {
        "price_weight": 0.4,
        "delivery_weight": 0.3,
        "compliance_weight": 0.3
    }
    
    print("\n" + "=" * 70)
    print("INTEGRATION TEST: SCORING WITH FALLBACK ONLY (NO OLLAMA)")
    print("=" * 70)
    
    try:
        print("\nScoring vendors (Ollama will be unavailable, using fallback)...\n")
        
        scored_vendors, summary = ScoringService.score_all_vendors(vendors, weights)
        
        print(f"✓ Successfully scored {len(scored_vendors)} vendors\n")
        
        # Verify results
        all_valid = True
        for i, vendor in enumerate(scored_vendors, 1):
            scores = vendor.get("scores", {})
            vendor_name = vendor.get("vendor_name", "Unknown")
            
            print(f"Vendor {i}: {vendor_name}")
            print(f"  │")
            print(f"  ├─ Price Score: {scores.get('price_score', 'N/A')}/10")
            print(f"  │  └─ {scores.get('price_justification', 'N/A')}")
            print(f"  │")
            print(f"  ├─ Delivery Score: {scores.get('delivery_score', 'N/A')}/10")
            print(f"  │  └─ {scores.get('delivery_justification', 'N/A')}")
            print(f"  │")
            print(f"  ├─ Compliance Score: {scores.get('compliance_score', 'N/A')}/10")
            print(f"  │  └─ {scores.get('compliance_justification', 'N/A')}")
            print(f"  │")
            print(f"  └─ Weighted Score: {scores.get('weighted_score', 'N/A')}/100")
            
            # Validate
            price_score = scores.get('price_score', 0)
            delivery_score = scores.get('delivery_score', 0)
            compliance_score = scores.get('compliance_score', 0)
            weighted_score = scores.get('weighted_score', 0)
            
            is_valid = (
                isinstance(price_score, int) and 1 <= price_score <= 10 and
                isinstance(delivery_score, int) and 1 <= delivery_score <= 10 and
                isinstance(compliance_score, int) and 1 <= compliance_score <= 10 and
                isinstance(weighted_score, (int, float)) and 0 <= weighted_score <= 100 and
                'price_justification' in scores and
                'delivery_justification' in scores and
                'compliance_justification' in scores and
                'overall_justification' in scores
            )
            
            print(f"  Status: {'✓ VALID' if is_valid else '✗ INVALID'}\n")
            
            if not is_valid:
                all_valid = False
                print(f"  ERROR: Invalid scores detected!")
                print(f"    price_score={price_score}, type={type(price_score)}")
                print(f"    delivery_score={delivery_score}, type={type(delivery_score)}")
                print(f"    compliance_score={compliance_score}, type={type(compliance_score)}")
                print(f"    weighted_score={weighted_score}, type={type(weighted_score)}\n")
        
        # Verify summary
        print(f"Summary Statistics:")
        print(f"  ├─ Total Vendors: {summary.get('total_vendors')}")
        print(f"  ├─ Average Score: {summary.get('average_score')}/100")
        print(f"  ├─ Max Score: {summary.get('max_score')}/100")
        print(f"  └─ Min Score: {summary.get('min_score')}/100")
        
        print("\n" + "=" * 70)
        if all_valid and summary.get('total_vendors') == len(scored_vendors):
            print("✓✓✓ ALL TESTS PASSED ✓✓✓")
            print("=" * 70)
            return True
        else:
            print("✗✗✗ TESTS FAILED ✗✗✗")
            print("=" * 70)
            return False
        
    except Exception as e:
        print(f"\n✗ TEST FAILED WITH EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_scoring_with_fallback_only()
    sys.exit(0 if success else 1)
