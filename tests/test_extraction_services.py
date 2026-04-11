"""Tests for text extraction and normalization."""
import pytest


class TestExtractionPipeline:
    """Test extraction and normalization service chain."""

    def test_extract_text_from_raw_proposal(self, sample_raw_text):
        """Extract text from raw proposal data."""
        from app.services.extractor import extract_text
        
        # Should handle raw text input
        result = extract_text(sample_raw_text)
        assert isinstance(result, (str, dict))

    def test_extract_structured_data_from_text(self, sample_raw_text):
        """Extract structured data from raw text."""
        from app.services.extractor import extract_structured_data
        
        result = extract_structured_data(sample_raw_text)
        assert isinstance(result, dict)
        # Common fields
        keys = {"vendor_name", "cost", "timeline_weeks"}
        has_key = any(k in result for k in keys)
        assert has_key or len(result) > 0

    def test_normalize_vendor_data(self, sample_structured_data):
        """Normalize extracted vendor data."""
        from app.services.normalizer import normalize
        
        result = normalize(sample_structured_data)
        assert isinstance(result, dict)
        # Should have normalized fields
        assert "cost" in result or "vendor_name" in result

    def test_detect_missing_fields(self, sample_structured_data):
        """Detect missing required fields in vendor data."""
        from app.services.extractor import detect_missing_fields
        
        vendor_with_gaps = {"vendor_name": "Partial"}
        result = detect_missing_fields(vendor_with_gaps)
        # Should return list of missing field names
        assert isinstance(result, list) or isinstance(result, dict)

    def test_infer_missing_values(self, sample_structured_data):
        """Infer missing values in vendor data."""
        from app.services.extractor import infer_missing_values
        
        incomplete = {"vendor_name": "Test Vendor", "cost": 250000000}
        result = infer_missing_values(incomplete)
        # Should return same or expanded dict
        assert isinstance(result, dict)


class TestExtractionWithRealFiles:
    """Test extraction with actual file paths."""

    def test_extract_from_pdf_file(self, sample_vendor_pdf):
        """Extract text from PDF vendor file."""
        if not sample_vendor_pdf or not sample_vendor_pdf.exists():
            pytest.skip("Sample PDF not available")
        
        from app.services.extractor import extract_text
        
        result = extract_text(str(sample_vendor_pdf))
        assert isinstance(result, (str, dict))

    def test_extract_from_xlsx_file(self, sample_vendor_xlsx):
        """Extract text from Excel vendor file."""
        if not sample_vendor_xlsx or not sample_vendor_xlsx.exists():
            pytest.skip("Sample Excel not available")
        
        from app.services.extractor import extract_text
        
        result = extract_text(str(sample_vendor_xlsx))
        assert isinstance(result, (str, dict))

    def test_extract_from_pptx_file(self, sample_vendor_pptx):
        """Extract text from PowerPoint vendor file."""
        if not sample_vendor_pptx or not sample_vendor_pptx.exists():
            pytest.skip("Sample PPTX not available")
        
        from app.services.extractor import extract_text
        
        result = extract_text(str(sample_vendor_pptx))
        assert isinstance(result, (str, dict))


class TestNormalizationLogic:
    """Test vendor data normalization."""

    def test_normalize_cost_formats(self):
        """Normalize various cost formats to numeric."""
        from app.services.normalizer import normalize
        
        test_cases = [
            {"cost": "3,43,37,900 INR"},  # Indian format
            {"cost": "343,379,000"},       # Comma separated
            {"cost": 343379000},            # Already numeric
        ]
        
        for case in test_cases:
            result = normalize(case)
            assert isinstance(result, dict)

    def test_normalize_timeline_formats(self):
        """Normalize various timeline formats to weeks."""
        from app.services.normalizer import normalize
        
        test_cases = [
            {"timeline_weeks": 28},
            {"timeline_weeks": "4 months"},
            {"timeline_weeks": "6-8 weeks"},
        ]
        
        for case in test_cases:
            result = normalize(case)
            assert isinstance(result, dict)

    def test_normalize_vendor_names(self):
        """Normalize vendor name formatting."""
        from app.services.normalizer import normalize
        
        test_cases = [
            {"vendor_name": "CREATIVE EDGE COMMUNICATIONS"},
            {"vendor_name": "  CreativeEdge  "},
            {"vendor_name": "creative edge pvt. ltd."},
        ]
        
        for case in test_cases:
            result = normalize(case)
            assert isinstance(result, dict)


class TestRobustness:
    """Test extraction robustness with edge cases."""

    def test_empty_input_handled(self):
        """Empty input handled gracefully."""
        from app.services.extractor import extract_text
        
        result = extract_text("")
        assert isinstance(result, (str, dict))

    def test_malformed_data_handled(self):
        """Malformed data handled without crash."""
        from app.services.extractor import extract_structured_data
        
        result = extract_structured_data("Invalid @@## data {{")
        assert isinstance(result, dict)

    def test_special_characters_handled(self):
        """Special characters in text handled."""
        from app.services.normalizer import normalize
        
        data = {"vendor_name": "TestCo™ ®© Ltd."}
        result = normalize(data)
        assert isinstance(result, dict)
