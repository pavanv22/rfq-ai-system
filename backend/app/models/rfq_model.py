from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import List, Optional
from .database import Base


# ==================== SQLAlchemy ORM Models ====================

class RFQModel(Base):
    """SQLAlchemy ORM model for RFQ."""
    __tablename__ = "rfqs"

    id = Column(String(36), primary_key=True)
    project_name = Column(String(255), nullable=False)
    scope = Column(Text, nullable=True)
    budget = Column(Float, nullable=False)
    currency = Column(String(10), default="USD")
    timeline_weeks = Column(Integer, nullable=False)
    sourcing_type = Column(String(100), nullable=True)  # e.g., "Individual", "Grouped"
    status = Column(String(50), default="pending")  # pending, active, closed
    requirements = Column(JSON, nullable=True)  # List of vendor requirements
    line_items = Column(JSON, nullable=True)  # List of line items
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    vendors = relationship("VendorModel", back_populates="rfq", cascade="all, delete-orphan")
    questionnaire = relationship("QuestionnaireModel", back_populates="rfq", uselist=False, cascade="all, delete-orphan")
    scores = relationship("ScoreModel", back_populates="rfq", cascade="all, delete-orphan")


# ==================== Pydantic Request/Response Schemas ====================

class RFQBase(BaseModel):
    """Base schema for RFQ validation."""
    project_name: str
    scope: Optional[str] = None
    budget: float
    currency: str = "USD"
    timeline_weeks: int
    sourcing_type: Optional[str] = None
    requirements: Optional[List[str]] = None
    line_items: Optional[List[dict]] = None


class RFQCreate(RFQBase):
    """Schema for creating a new RFQ."""
    pass


class RFQUpdate(BaseModel):
    """Schema for updating an RFQ."""
    project_name: Optional[str] = None
    scope: Optional[str] = None
    budget: Optional[float] = None
    currency: Optional[str] = None
    timeline_weeks: Optional[int] = None
    sourcing_type: Optional[str] = None
    status: Optional[str] = None
    requirements: Optional[List[str]] = None
    line_items: Optional[List[dict]] = None


class RFQResponse(RFQBase):
    """Schema for RFQ response."""
    id: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
