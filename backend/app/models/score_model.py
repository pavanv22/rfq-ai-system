from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import Optional
from .database import Base


# ==================== SQLAlchemy ORM Models ====================

class ScoreModel(Base):
    """SQLAlchemy ORM model for Vendor Scoring Results."""
    __tablename__ = "scores"

    id = Column(String(36), primary_key=True)
    rfq_id = Column(String(36), ForeignKey("rfqs.id"), nullable=False)
    vendor_id = Column(String(36), ForeignKey("vendors.id"), nullable=False)
    
    # Individual criterion scores (0-10)
    price_score = Column(Integer, nullable=True)
    delivery_score = Column(Integer, nullable=True)
    compliance_score = Column(Integer, nullable=True)
    
    # Weighted final score
    weighted_score = Column(Float, nullable=True)  # Final 0-100 score
    rank = Column(Integer, nullable=True)  # Ranking among vendors for this RFQ
    
    # Justifications
    price_justification = Column(Text, nullable=True)
    delivery_justification = Column(Text, nullable=True)
    compliance_justification = Column(Text, nullable=True)
    overall_justification = Column(Text, nullable=True)
    
    # AI scoring metadata
    score_details = Column(JSON, nullable=True)  # Additional scoring details
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    rfq = relationship("RFQModel", back_populates="scores")
    vendor = relationship("VendorModel", back_populates="scores")


# ==================== Pydantic Request/Response Schemas ====================

class ScoreCriterion(BaseModel):
    """Individual criterion score."""
    score: int  # 0-10
    justification: str


class ScoreBase(BaseModel):
    """Base schema for Score validation."""
    price_score: Optional[int] = None
    delivery_score: Optional[int] = None
    compliance_score: Optional[int] = None


class ScoreCreate(ScoreBase):
    """Schema for creating scores."""
    rfq_id: str
    vendor_id: str


class ScoreResponse(BaseModel):
    """Schema for score response."""
    id: str
    rfq_id: str
    vendor_id: str
    price_score: Optional[int]
    delivery_score: Optional[int]
    compliance_score: Optional[int]
    weighted_score: Optional[float]
    rank: Optional[int]
    price_justification: Optional[str]
    delivery_justification: Optional[str]
    compliance_justification: Optional[str]
    overall_justification: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ScoringWeights(BaseModel):
    """Scoring weights configuration."""
    price_weight: float = 0.4  # 40%
    delivery_weight: float = 0.3  # 30%
    compliance_weight: float = 0.3  # 30%

    def __post_init__(self):
        """Validate that weights sum to 1.0."""
        total = self.price_weight + self.delivery_weight + self.compliance_weight
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {total}")
