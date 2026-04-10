from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, Text, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import List, Optional
from .database import Base


# ==================== SQLAlchemy ORM Models ====================

class VendorModel(Base):
    """SQLAlchemy ORM model for Vendor."""
    __tablename__ = "vendors"

    id = Column(String(36), primary_key=True)
    rfq_id = Column(String(36), ForeignKey("rfqs.id"), nullable=False)
    vendor_name = Column(String(255), nullable=False)
    total_cost = Column(Float, nullable=True)
    currency = Column(String(10), default="USD")
    currency_normalized = Column(String(10), default="USD")
    total_cost_usd = Column(Float, nullable=True)  # Normalized to USD
    timeline_weeks = Column(Integer, nullable=True)
    scope_coverage = Column(JSON, nullable=True)  # List of covered items
    compliance_score = Column(Integer, nullable=True)  # 0-10
    key_terms = Column(JSON, nullable=True)  # Important terms from submission
    raw_extracted_data = Column(JSON, nullable=True)  # Raw extracted data before normalization
    normalized_data = Column(JSON, nullable=True)  # Normalized data
    extraction_status = Column(String(50), default="pending")  # pending, extracted, normalized, incomplete
    missing_fields = Column(JSON, nullable=True)  # Which fields are missing
    ai_inferred_fields = Column(Boolean, default=False)  # Were missing fields inferred by AI?
    file_path = Column(String(500), nullable=True)  # Path to uploaded file
    file_type = Column(String(50), nullable=True)  # pdf, docx, pptx, xlsx, png, jpg, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    rfq = relationship("RFQModel", back_populates="vendors")
    scores = relationship("ScoreModel", back_populates="vendor", cascade="all, delete-orphan")


# ==================== Pydantic Request/Response Schemas ====================

class VendorBase(BaseModel):
    """Base schema for Vendor validation."""
    vendor_name: str
    total_cost: Optional[float] = None
    currency: str = "USD"
    timeline_weeks: Optional[int] = None
    scope_coverage: Optional[List[str]] = None
    key_terms: Optional[List[str]] = None


class VendorCreate(VendorBase):
    """Schema for creating a new vendor entry."""
    rfq_id: str


class VendorUpdate(BaseModel):
    """Schema for updating vendor data."""
    vendor_name: Optional[str] = None
    total_cost: Optional[float] = None
    currency: Optional[str] = None
    timeline_weeks: Optional[int] = None
    scope_coverage: Optional[List[str]] = None
    key_terms: Optional[List[str]] = None


class VendorResponse(VendorBase):
    """Schema for vendor response."""
    id: str
    rfq_id: str
    currency_normalized: str
    total_cost_usd: Optional[float]
    compliance_score: Optional[int]
    extraction_status: str
    missing_fields: Optional[List[str]]
    ai_inferred_fields: bool
    file_type: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
