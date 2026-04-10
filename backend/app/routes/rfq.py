from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.models import (
    RFQModel, RFQCreate, RFQUpdate, RFQResponse,
    QuestionnaireModel, QuestionnaireCreate, QuestionnaireResponse,
    get_db
)
from app.agents.questionnaire_agent import generate_questionnaire

router = APIRouter(tags=["RFQ"])


# ==================== RFQ Endpoints ====================

@router.post("/", response_model=RFQResponse, status_code=status.HTTP_201_CREATED)
def create_rfq(rfq_data: RFQCreate, db: Session = Depends(get_db)):
    """Create a new RFQ."""
    try:
        rfq = RFQModel(
            id=str(uuid.uuid4()),
            **rfq_data.dict()
        )
        db.add(rfq)
        db.commit()
        db.refresh(rfq)
        return rfq
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating RFQ: {str(e)}"
        )


@router.get("/", response_model=List[RFQResponse])
def list_rfqs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all RFQs with pagination."""
    try:
        rfqs = db.query(RFQModel).offset(skip).limit(limit).all()
        return rfqs
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching RFQs: {str(e)}"
        )


@router.get("/{rfq_id}", response_model=RFQResponse)
def get_rfq(rfq_id: str, db: Session = Depends(get_db)):
    """Get a single RFQ by ID."""
    try:
        rfq = db.query(RFQModel).filter(RFQModel.id == rfq_id).first()
        if not rfq:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"RFQ with ID {rfq_id} not found"
            )
        return rfq
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching RFQ: {str(e)}"
        )


@router.put("/{rfq_id}", response_model=RFQResponse)
def update_rfq(rfq_id: str, rfq_data: RFQUpdate, db: Session = Depends(get_db)):
    """Update an existing RFQ."""
    try:
        rfq = db.query(RFQModel).filter(RFQModel.id == rfq_id).first()
        if not rfq:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"RFQ with ID {rfq_id} not found"
            )
        
        # Update only provided fields
        update_data = rfq_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(rfq, field, value)
        
        db.commit()
        db.refresh(rfq)
        return rfq
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating RFQ: {str(e)}"
        )


@router.delete("/{rfq_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rfq(rfq_id: str, db: Session = Depends(get_db)):
    """Delete an RFQ by ID."""
    try:
        rfq = db.query(RFQModel).filter(RFQModel.id == rfq_id).first()
        if not rfq:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"RFQ with ID {rfq_id} not found"
            )
        
        db.delete(rfq)
        db.commit()
        return None
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting RFQ: {str(e)}"
        )


# ==================== Questionnaire Endpoints ====================

@router.post("/{rfq_id}/generate-questions", response_model=QuestionnaireResponse)
def generate_questions_for_rfq(rfq_id: str, db: Session = Depends(get_db)):
    """Generate AI questionnaire for an RFQ."""
    try:
        # Fetch the RFQ
        rfq = db.query(RFQModel).filter(RFQModel.id == rfq_id).first()
        if not rfq:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"RFQ with ID {rfq_id} not found"
            )
        
        # Check if questionnaire already exists
        existing_q = db.query(QuestionnaireModel).filter(
            QuestionnaireModel.rfq_id == rfq_id
        ).first()
        if existing_q:
            return existing_q
        
        # Generate questionnaire using AI agent
        questions_result = generate_questionnaire(rfq)
        
        # Extract questions and metadata
        questions = questions_result.get("questions", [])
        raw_prompt = questions_result.get("prompt", "")
        raw_response = questions_result.get("raw_response", "")
        
        # Create and save questionnaire
        questionnaire = QuestionnaireModel(
            id=str(uuid.uuid4()),
            rfq_id=rfq_id,
            questions=questions,
            raw_prompt=raw_prompt,
            raw_response=raw_response
        )
        db.add(questionnaire)
        db.commit()
        db.refresh(questionnaire)
        
        return questionnaire
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating questionnaire: {str(e)}"
        )


@router.get("/{rfq_id}/questions", response_model=QuestionnaireResponse)
def get_questionnaire(rfq_id: str, db: Session = Depends(get_db)):
    """Retrieve questionnaire for an RFQ."""
    try:
        questionnaire = db.query(QuestionnaireModel).filter(
            QuestionnaireModel.rfq_id == rfq_id
        ).first()
        if not questionnaire:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Questionnaire for RFQ {rfq_id} not found"
            )
        return questionnaire
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching questionnaire: {str(e)}"
        )
