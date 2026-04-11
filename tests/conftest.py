import pytest
from pathlib import Path
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Setup Python path - must be done before any imports from app
backend_path = Path(__file__).parent.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

# Import models and app
try:
    from app.models.database import Base
    from app.models import RFQModel, VendorModel
    from app.main import app
except ImportError as e:
    print(f"Import error: {e}")
    print(f"Backend path: {backend_path}")
    print(f"Backend exists: {backend_path.exists()}")
    print(f"sys.path: {sys.path}")
    raise

# Test database
TEST_DATABASE_URL = "sqlite:///./test_rfq_system.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def clean_db():
    """Clear and recreate database for each test."""
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def db(clean_db):
    """Provide a database session for tests."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(clean_db):
    """Provide a FastAPI TestClient with clean database."""
    return TestClient(app)


@pytest.fixture
def test_rfq(db):
    """Create a test RFQ."""
    rfq = RFQModel(
        id="test-rfq-001",
        project_name="Test RFQ: Global Launch - New Kids Health Drink",
        scope="Integrated Marketing Campaign",
        budget=1000000.0,
        currency="USD",
        sourcing_type="Competitive Bid",
        timeline_weeks=28,
        line_items=[],
        requirements=["ISO certified", "child safety compliance"]
    )
    db.add(rfq)
    db.commit()
    db.refresh(rfq)
    return rfq


@pytest.fixture
def test_vendor(db, test_rfq):
    """Create a test vendor record."""
    vendor = VendorModel(
        id="test-vendor-001",
        rfq_id=test_rfq.id,
        vendor_name="Test Vendor Inc",
        total_cost=250000000.0,
        currency="INR",
        currency_normalized="USD",
        total_cost_usd=3000000.0,
        timeline_weeks=20,
        scope_coverage=["Full service marketing", "Digital campaign"],
        key_terms=["ISO certified"],
        file_path="/test/files/test_vendor.pdf",
        file_type="pdf",
        extraction_status="normalized"
    )
    db.add(vendor)
    db.commit()
    db.refresh(vendor)
    return vendor


@pytest.fixture
def sample_vendor_pdf():
    """Return path to sample vendor PDF fixture."""
    return Path(__file__).parent / "fixtures" / "Vendor1_CreativeEdge_Proposal.pdf"


@pytest.fixture
def sample_vendor_xlsx():
    """Return path to sample vendor Excel fixture."""
    return Path(__file__).parent / "fixtures" / "Vendor3_BrandSpark_Quotation.xlsx"


@pytest.fixture
def sample_vendor_pptx():
    """Return path to sample vendor PowerPoint fixture."""
    return Path(__file__).parent / "fixtures" / "Vendor2_MediaPulse_Proposal.pptx"


@pytest.fixture
def test_rfq_dict():
    """Return test RFQ as dict (for testing agent inputs)."""
    return {
        "id": "test-rfq-001",
        "project_name": "Global Launch - New Kids Health Drink",
        "subject": "Marketing RFQ",
        "scope": "Full integrated marketing: strategy, creative, TVC, digital",
        "sourcing_type": "Competitive",
        "timeline_weeks": 28,
        "line_items": [
            {"desc": "Strategy & Creative", "cost": 44650000},
            {"desc": "TVC Production", "cost": 55400000},
            {"desc": "Digital Content", "cost": 102600000},
            {"desc": "Compliance & Management", "cost": 71400000}
        ],
        "requirements": "ISO 9001, child safety compliance required",
        "vendor_requirements": "Experience with kids campaigns, ISOs"
    }


@pytest.fixture
def sample_raw_text():
    """Return sample extracted text from a vendor proposal."""
    return """RFQ-MKT-KIDS-GL-2026-001
CreativeEdge Communications Pvt. Ltd.
Cost: 3,43,37,900 INR
Timeline: 28 weeks
Contact: Rajesh Mehta, r.mehta@creativeedge.in
Scope: Integrated Marketing, TVC Production, Digital, Media Planning"""


@pytest.fixture
def sample_structured_data():
    """Return sample structured extraction data."""
    return {
        "vendor_name": "CreativeEdge Communications Pvt Ltd",
        "cost": 343379000,
        "currency": "INR",
        "timeline_weeks": 28,
        "scope": "Integrated Marketing, TVC Production, Digital, Media Planning",
        "contact_name": "Rajesh Mehta",
        "contact_email": "r.mehta@creativeedge.in",
        "rfq_id": "RFQ-MKT-KIDS-GL-2026-001"
    }
