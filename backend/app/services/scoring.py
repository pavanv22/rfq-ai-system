"""
Vendor scoring service - computes weighted scores across multiple criteria.
"""

from typing import List, Dict, Tuple
from app.agents.scoring_agent import score_vendor


class ScoringService:
    """Service to compute weighted vendor scores."""
    
    # Default scoring weights (40% price, 30% delivery, 30% compliance)
    DEFAULT_WEIGHTS = {
        "price_weight": 0.4,
        "delivery_weight": 0.3,
        "compliance_weight": 0.3
    }
    
    @staticmethod
    def score_vendor(vendor_data: Dict, weights: Dict = None) -> Dict:
        """
        Score a single vendor using the scoring agent.
        
        Args:
            vendor_data: Vendor data dictionary
            weights: Optional custom scoring weights
        
        Returns:
            Score results including individual criteria scores and weighted total
        """
        if weights is None:
            weights = ScoringService.DEFAULT_WEIGHTS
        
        return score_vendor(vendor_data, weights)
    
    @staticmethod
    def score_all_vendors(
        vendors: List[Dict],
        weights: Dict = None
    ) -> Tuple[List[Dict], Dict]:
        """
        Score all vendors in a list.
        
        Args:
            vendors: List of vendor data dictionaries
            weights: Optional custom scoring weights
        
        Returns:
            Tuple of (scored_vendors_list, scoring_summary)
        """
        if weights is None:
            weights = ScoringService.DEFAULT_WEIGHTS
        
        results = []
        
        for vendor in vendors:
            try:
                score_data = ScoringService.score_vendor(vendor, weights)
                vendor["scores"] = score_data
                results.append(vendor)
            except Exception as e:
                print(f"Error scoring vendor {vendor.get('vendor_name', 'Unknown')}: {e}")
                # Add fallback scores
                vendor["scores"] = {
                    "price_score": 5,
                    "delivery_score": 5,
                    "compliance_score": 5,
                    "weighted_score": 50.0,
                    "overall_justification": f"Scoring error: {str(e)}"
                }
                results.append(vendor)
        
        # Calculate summary statistics
        summary = ScoringService._calculate_summary(results)
        
        return results, summary
    
    @staticmethod
    def _calculate_summary(vendors: List[Dict]) -> Dict:
        """Calculate summary statistics for all vendor scores."""
        if not vendors:
            return {}
        
        weighted_scores = [
            v.get("scores", {}).get("weighted_score", 0)
            for v in vendors
        ]
        
        return {
            "total_vendors": len(vendors),
            "average_score": round(sum(weighted_scores) / len(weighted_scores), 2) if weighted_scores else 0,
            "max_score": max(weighted_scores) if weighted_scores else 0,
            "min_score": min(weighted_scores) if weighted_scores else 0,
        }


def compute_score(vendors: List[Dict], weights: Dict = None) -> List[Dict]:
    """
    Backward-compatible function to compute scores for a list of vendors.
    
    Args:
        vendors: List of vendor data
        weights: Optional custom scoring weights
    
    Returns:
        List of vendors with scores
    """
    results, _ = ScoringService.score_all_vendors(vendors, weights)
    return results
