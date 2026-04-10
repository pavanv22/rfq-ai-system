"""
Decision agent - recommends best vendor and provides rankings.
"""

from typing import List, Dict, Tuple


def rank_vendors(vendors: List[Dict]) -> Tuple[List[Dict], Dict]:
    """
    Rank vendors by weighted score.
    
    Args:
        vendors: List of vendor data with scores
    
    Returns:
        Tuple of (ranked_vendors, best_vendor_recommendation)
    """
    if not vendors:
        return [], {
            "message": "No vendor data available. Please upload vendor files first.",
            "best_vendor": None,
            "ranking": []
        }
    
    # Sort vendors by weighted score (descending)
    ranked = sorted(
        vendors,
        key=lambda x: x.get("scores", {}).get("weighted_score", 0),
        reverse=True
    )
    
    # Add ranking position to each vendor
    for idx, vendor in enumerate(ranked, 1):
        vendor["rank"] = idx
    
    return ranked, ranked[0] if ranked else None


def generate_comparison_matrix(vendors: List[Dict]) -> Dict:
    """
    Generate a comparison matrix for all vendors across all criteria.
    
    Args:
        vendors: List of vendor data with scores
    
    Returns:
        Dictionary with comparison data
    """
    if not vendors:
        return {}
    
    comparison = {
        "vendors": [],
        "criteria": ["Price", "Delivery", "Compliance", "Weighted Score"],
    }
    
    for vendor in vendors:
        scores = vendor.get("scores", {})
        comparison["vendors"].append({
            "name": vendor.get("vendor_name", "Unknown"),
            "id": vendor.get("id", ""),
            "scores": [
                scores.get("price_score", 0),
                scores.get("delivery_score", 0),
                scores.get("compliance_score", 0),
                scores.get("weighted_score", 0),
            ],
            "rank": vendor.get("rank", 0),
            "justifications": {
                "price": scores.get("price_justification", ""),
                "delivery": scores.get("delivery_justification", ""),
                "compliance": scores.get("compliance_justification", ""),
                "overall": scores.get("overall_justification", "")
            }
        })
    
    return comparison


def generate_award_recommendation(
    ranked_vendors: List[Dict],
    rfq_data: Dict = None
) -> Dict:
    """
    Generate detailed award recommendation for the best vendor.
    
    Args:
        ranked_vendors: Ranked list of vendors
        rfq_data: Optional RFQ data for context
    
    Returns:
        Award recommendation dictionary
    """
    if not ranked_vendors:
        return {
            "award_recommendation": None,
            "reason": "No vendors available for recommendation"
        }
    
    best_vendor = ranked_vendors[0]
    scores = best_vendor.get("scores", {})
    
    recommendation = {
        "award_recommendation": {
            "vendor_name": best_vendor.get("vendor_name", "Unknown"),
            "vendor_id": best_vendor.get("id", ""),
            "rank": 1,
            "weighted_score": scores.get("weighted_score", 0),
            "price_score": scores.get("price_score", 0),
            "delivery_score": scores.get("delivery_score", 0),
            "compliance_score": scores.get("compliance_score", 0),
        },
        "reasons": [
            scores.get("overall_justification", "Highest weighted score"),
            f"Price: {scores.get('price_justification', 'N/A')}",
            f"Delivery: {scores.get('delivery_justification', 'N/A')}",
            f"Compliance: {scores.get('compliance_justification', 'N/A')}"
        ],
        "runner_ups": []
    }
    
    # Add runner-ups
    for vendor in ranked_vendors[1:4]:  # Top 3 alternatives
        alt_scores = vendor.get("scores", {})
        recommendation["runner_ups"].append({
            "vendor_name": vendor.get("vendor_name", "Unknown"),
            "vendor_id": vendor.get("id", ""),
            "rank": vendor.get("rank", 0),
            "weighted_score": alt_scores.get("weighted_score", 0),
            "score_gap": round(
                scores.get("weighted_score", 0) - alt_scores.get("weighted_score", 0),
                2
            )
        })
    
    return recommendation


def recommend(vendors: List[Dict], rfq_data: Dict = None) -> Dict:
    """
    Main recommendation function - provides ranking and award decision.
    
    Args:
        vendors: List of vendor data (with scores)
        rfq_data: Optional RFQ context data
    
    Returns:
        Comprehensive recommendation dictionary
    """
    if not vendors:
        return {
            "message": "No vendor data available. Please upload vendor files first.",
            "best_vendor": None,
            "ranking": [],
            "comparison": {}
        }
    
    # Rank vendors
    ranked, best = rank_vendors(vendors)
    
    # Generate comparison matrix
    comparison = generate_comparison_matrix(ranked)
    
    # Generate award recommendation
    award = generate_award_recommendation(ranked, rfq_data)
    
    return {
        "message": "Recommendation generated successfully",
        "best_vendor": best,
        "ranking": ranked,
        "comparison_matrix": comparison,
        "award_recommendation": award,
        "total_vendors_evaluated": len(vendors)
    }
