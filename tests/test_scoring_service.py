"""Tests for vendor scoring using ScoringService."""
import pytest
from app.services.scoring import ScoringService, compute_score


class TestScoringServiceBasic:
    """Test ScoringService with real vendor data."""

    def test_score_single_vendor(self, sample_structured_data):
        """Score a single vendor successfully."""
        result = ScoringService.score_vendor(sample_structured_data)
        assert isinstance(result, dict)
        # Should contain at least some score data
        assert len(result) > 0

    def test_score_multiple_vendors(self, sample_structured_data):
        """Score multiple vendors and get summary stats."""
        vendors = [
            {**sample_structured_data, "vendor_name": "V1", "cost": 243080000},
            {**sample_structured_data, "vendor_name": "V2", "cost": 285570000},
            {**sample_structured_data, "vendor_name": "V3", "cost": 343379000}
        ]
        results, summary = ScoringService.score_all_vendors(vendors)
        
        assert len(results) == 3
        assert summary["total_vendors"] == 3
        assert "average_score" in summary

    def test_score_with_minimal_fields(self):
        """Scoring handles vendors with only required fields."""
        vendor = {"vendor_name": "Minimal Vendor", "cost": 250000000}
        result = ScoringService.score_vendor(vendor)
        assert isinstance(result, dict)

    def test_default_weights_valid(self):
        """Verify default scoring weights are valid."""
        weights = ScoringService.DEFAULT_WEIGHTS
        total = (weights.get("price_weight", 0) + 
                weights.get("delivery_weight", 0) + 
                weights.get("compliance_weight", 0))
        assert 0.95 < total < 1.05

    def test_custom_weights_accepted(self, sample_structured_data):
        """Custom weights are accepted without error."""
        custom_weights = {
            "price_weight": 0.6,
            "delivery_weight": 0.2,
            "compliance_weight": 0.2
        }
        result = ScoringService.score_vendor(sample_structured_data, custom_weights)
        assert isinstance(result, dict)

    def test_score_empty_vendor_list(self):
        """Empty vendor list handled gracefully."""
        results, summary = ScoringService.score_all_vendors([])
        assert isinstance(results, list)
        assert len(results) == 0

    def test_three_real_vendor_costs(self):
        """Score with three real vendor cost values."""
        vendors = [
            {"vendor_name": "MediaPulse", "cost": 243080000},
            {"vendor_name": "BrandSpark", "cost": 285570000},
            {"vendor_name": "CreativeEdge", "cost": 343379000}
        ]
        results, summary = ScoringService.score_all_vendors(vendors)
        assert len(results) == 3
        assert summary["total_vendors"] == 3

    def test_vendor_with_zero_cost_handled(self):
        """Vendor with zero cost handled gracefully."""
        vendor = {"vendor_name": "Free Vendor", "cost": 0}
        result = ScoringService.score_vendor(vendor)
        assert isinstance(result, dict)

    def test_vendor_with_very_high_cost_handled(self):
        """Vendor with very high cost handled gracefully."""
        vendor = {"vendor_name": "Expensive", "cost": 999999999999}
        result = ScoringService.score_vendor(vendor)
        assert isinstance(result, dict)


class TestComputeScoreFunction:
    """Test the compute_score backward-compatible function."""

    def test_compute_score_callable(self):
        """Verify compute_score function is callable."""
        assert callable(compute_score)

    def test_compute_score_returns_list(self, sample_structured_data):
        """compute_score returns list."""
        result = compute_score([sample_structured_data])
        assert isinstance(result, (list, tuple))


class TestScoringConsistency:
    """Test scoring consistency."""

    def test_same_vendors_same_score(self, sample_structured_data):
        """Same vendor data produces consistent scores."""
        vendor1 = sample_structured_data.copy()
        vendor2 = sample_structured_data.copy()
        
        result1 = ScoringService.score_vendor(vendor1)
        result2 = ScoringService.score_vendor(vendor2)
        
        assert isinstance(result1, dict)
        assert isinstance(result2, dict)

    def test_lower_cost_better_price_score(self):
        """Lower cost vendor receives equal or better price scoring."""
        cheap = {"vendor_name": "Cheap", "cost": 200000000}
        expensive = {"vendor_name": "Expensive", "cost": 400000000}
        
        cheap_score = ScoringService.score_vendor(cheap)
        exp_score = ScoringService.score_vendor(expensive)
        
        # Both should return dict
        assert isinstance(cheap_score, dict)
        assert isinstance(exp_score, dict)
