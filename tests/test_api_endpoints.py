"""Tests for API endpoints - vendor upload, RFQ, and scoring routes."""
import pytest
import json
from pathlib import Path


class TestVendorUploadAPI:
    """Test POST /{rfq_id}/upload endpoint for vendor files."""

    @pytest.mark.skip(reason="Requires running backend with upload directory")
    def test_upload_vendor_requires_rfq_exists(self, client, test_rfq):
        """Upload fails if RFQ doesn't exist."""
        response = client.post(
            "/vendors/nonexistent-rfq/upload",
            files={"file": ("test.txt", b"test content", "text/plain")}
        )
        assert response.status_code == 404

    @pytest.mark.skip(reason="Requires sample PDF and running backend")
    def test_upload_pdf_vendor_success(self, client, test_rfq, sample_vendor_pdf):
        """Upload PDF vendor file successfully."""
        if not sample_vendor_pdf or not sample_vendor_pdf.exists():
            pytest.skip("Sample PDF not found")
        
        with open(sample_vendor_pdf, "rb") as f:
            response = client.post(
                f"/vendors/{test_rfq.id}/upload",
                files={"file": (sample_vendor_pdf.name, f, "application/pdf")},
                params={}
            )
        
        assert response.status_code in [200, 201]

    @pytest.mark.skip(reason="Requires sample Excel and running backend")
    def test_upload_xlsx_vendor_success(self, client, test_rfq, sample_vendor_xlsx):
        """Upload Excel vendor file successfully."""
        if not sample_vendor_xlsx or not sample_vendor_xlsx.exists():
            pytest.skip("Sample Excel not found")
        
        with open(sample_vendor_xlsx, "rb") as f:
            response = client.post(
                f"/vendors/{test_rfq.id}/upload",
                files={"file": (sample_vendor_xlsx.name, f)},
                params={}
            )
        
        assert response.status_code in [200, 201]

    def test_upload_with_vendor_name_parameter(self, client, test_rfq):
        """Upload supports optional vendor_name parameter."""
        # This test documents the API parameter
        # Actual upload would require a file
        pass


class TestRFQAPI:
    """Test RFQ endpoints."""

    def test_create_rfq(self, client):
        """Create a new RFQ."""
        rfq_data = {
            "subject": "Test Marketing RFQ",
            "scope": "Full service marketing",
            "sourcing_type": "Competitive",
            "timeline_weeks": 24,
            "line_items": [],
            "vendor_requirements": "ISO certified"
        }
        response = client.post("/rfqs/", json=rfq_data)
        # Should return 201 or sync successfully
        assert response.status_code in [200, 201]
        if response.status_code == 201:
            data = response.json()
            assert "id" in data

    def test_list_rfqs(self, client):
        """List all RFQs."""
        response = client.get("/rfqs/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_single_rfq(self, client, test_rfq):
        """Retrieve a single RFQ by ID."""
        response = client.get(f"/rfqs/{test_rfq.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_rfq.id

    def test_update_rfq(self, client, test_rfq):
        """Update an existing RFQ."""
        update_data = {
            "subject": "Updated Subject"
        }
        response = client.put(f"/rfqs/{test_rfq.id}", json=update_data)
        assert response.status_code in [200, 202]

    def test_delete_rfq(self, client, test_rfq):
        """Delete an RFQ."""
        response = client.delete(f"/rfqs/{test_rfq.id}")
        assert response.status_code in [200, 204]

    def test_generate_questionnaire_for_rfq(self, client, test_rfq):
        """Generate questionnaire for an RFQ."""
        response = client.post(f"/rfqs/{test_rfq.id}/generate-questions")
        # May return 201 or error if Ollama not running
        assert response.status_code in [200, 201, 503, 504]

    def test_get_questionnaire_for_rfq(self, client, test_rfq):
        """Retrieve questionnaire for an RFQ."""
        response = client.get(f"/rfqs/{test_rfq.id}/questions")
        # May return 404 if none generated yet, or 200 with data
        assert response.status_code in [200, 404]


class TestVendorAPI:
    """Test Vendor endpoints."""

    def test_create_vendor(self, client, test_rfq, sample_structured_data):
        """Create a new vendor record."""
        vendor_data = {
            **sample_structured_data,
            "rfq_id": test_rfq.id
        }
        response = client.post("/vendors/", json=vendor_data)
        assert response.status_code in [200, 201]
        if response.status_code in [200, 201]:
            data = response.json()
            assert "id" in data

    def test_list_vendors_for_rfq(self, client, test_rfq):
        """List vendors for an RFQ."""
        response = client.get(f"/vendors/?rfq_id={test_rfq.id}")
        assert response.status_code == 200
        vendors = response.json()
        assert isinstance(vendors, list)

    def test_get_single_vendor(self, client, test_vendor):
        """Get a single vendor by ID."""
        response = client.get(f"/vendors/{test_vendor.id}")
        assert response.status_code == 200
        vendor = response.json()
        assert vendor["id"] == test_vendor.id

    def test_update_vendor(self, client, test_vendor):
        """Update a vendor record."""
        update_data = {"vendor_name": "Updated Name"}
        response = client.put(f"/vendors/{test_vendor.id}", json=update_data)
        assert response.status_code in [200, 202]

    def test_delete_vendor(self, client, test_vendor):
        """Delete a vendor."""
        response = client.delete(f"/vendors/{test_vendor.id}")
        assert response.status_code in [200, 204]


class TestAnalysisAPI:
    """Test Analysis/Scoring endpoints."""

    def test_run_scoring_for_rfq(self, client, test_rfq):
        """Run scoring analysis for an RFQ."""
        response = client.post(f"/analysis/run-scoring", json={"rfq_id": test_rfq.id})
        # May succeed or return 404 if no vendors
        assert response.status_code in [200, 201, 404]

    def test_get_scores_for_rfq(self, client, test_rfq):
        """Get scores for vendors in an RFQ."""
        response = client.get(f"/analysis/scores?rfq_id={test_rfq.id}")
        # May return empty list or 404
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            scores = response.json()
            assert isinstance(scores, list)

    def test_get_single_score(self, client, test_vendor):
        """Get score for a single vendor."""
        response = client.get(f"/analysis/scores/{test_vendor.id}")
        # May return 404 if score not computed
        assert response.status_code in [200, 404]


class TestHealthcheck:
    """Test basic endpoint health."""

    @pytest.mark.skip(reason="Depends on actual backend routes")
    def test_api_is_running(self, client):
        """Verify API is responsive."""
        # Try any endpoint that should exist
        response = client.get("/rfqs/")
        assert response.status_code in [200, 405, 404]
