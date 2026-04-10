from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import List, Optional
from .database import Base


# ==================== SQLAlchemy ORM Models ====================

class QuestionnaireModel(Base):
    """SQLAlchemy ORM model for AI-generated Questionnaire."""
    __tablename__ = "questionnaires"

    id = Column(String(36), primary_key=True)
    rfq_id = Column(String(36), ForeignKey("rfqs.id"), nullable=False, unique=True)
    questions = Column(JSON, nullable=False)  # List of Q&A objects
    raw_prompt = Column(Text, nullable=True)  # Prompt sent to LLM
    raw_response = Column(Text, nullable=True)  # Raw LLM response
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    rfq = relationship("RFQModel", back_populates="questionnaire")


# ==================== Pydantic Request/Response Schemas ====================

class QuestionDetail(BaseModel):
    """Individual question in the questionnaire."""
    question: str
    category: Optional[str] = None  # e.g., "compliance", "experience", "timeline", "pricing"
    required: bool = True


class QuestionnaireBase(BaseModel):
    """Base schema for Questionnaire validation."""
    questions: List[QuestionDetail]


class QuestionnaireCreate(QuestionnaireBase):
    """Schema for creating a questionnaire."""
    rfq_id: str
    raw_prompt: Optional[str] = None
    raw_response: Optional[str] = None


class QuestionnaireResponse(QuestionnaireBase):
    """Schema for questionnaire response."""
    id: str
    rfq_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
