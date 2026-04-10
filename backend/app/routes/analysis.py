"""
Analysis endpoints - scoring, ranking, and recommendations.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
import uuid

from app.models import (
    RFQModel, VendorModel, ScoreModel, ScoringWeights,
    ScoreCreate, ScoreResponse, get_db
)
from app.services.scoring import ScoringService
from app.agents.decision_agent import recommend

router = APIRouter(tags=["Analysis"])


# ==================== Scoring Endpoints ====================

@router.post("/{rfq_id}/score", status_code=status.HTTP_201_CREATED)
def run_scoring(
    rfq_id: str,
    price_weight: float = Query(0.4, ge=0, le=1),
    delivery_weight: float = Query(0.3, ge=0, le=1),
    compliance_weight: float = Query(0.3, ge=0, le=1),
    db: Session = Depends(get_db)
):
    """
    Run scoring for all vendors in an RFQ.
    
    Weights must sum to 1.0. Defaults: Price=40%, Delivery=30%, Compliance=30%
    """
    try:
        # Verify weights sum to 1.0
        total_weight = price_weight + delivery_weight + compliance_weight
        if abs(total_weight - 1.0) > 0.01:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Weights must sum to 1.0, got {total_weight}"
            )
        
        # Verify RFQ exists
        rfq = db.query(RFQModel).filter(RFQModel.id == rfq_id).first()
        if not rfq:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"RFQ with ID {rfq_id} not found"
            )
        
        # Fetch all vendors for this RFQ
        vendors = db.query(VendorModel).filter(
            VendorModel.rfq_id == rfq_id
        ).all()
        
        if not vendors:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"No vendors found for RFQ {rfq_id}"
            )
        
        # Prepare scoring weights
        weights = {
            "price_weight": price_weight,
            "delivery_weight": delivery_weight,
            "compliance_weight": compliance_weight
        }
        
        # Convert ORM models to dicts for scoring
        vendor_dicts = [
            {
                "id": v.id,
                "vendor_name": v.vendor_name,
                "total_cost": v.total_cost,
                "currency": v.currency,
                "total_cost_usd": v.total_cost_usd,
                "timeline_weeks": v.timeline_weeks,
                "scope_coverage": v.scope_coverage,
                "key_terms": v.key_terms,
                "compliance_score": v.compliance_score
            }
            for v in vendors
        ]
        
        # Score all vendors
        scored_vendors, summary = ScoringService.score_all_vendors(vendor_dicts, weights)
        
        # IMPORTANT: Sort vendors by weighted score (descending) to assign correct ranks
        scored_vendors = sorted(
            scored_vendors,
            key=lambda v: v.get("scores", {}).get("weighted_score", 0),
            reverse=True
        )
        
        # Save scores to database
        results = []
        for rank_idx, vendor_data in enumerate(scored_vendors):
            scores = vendor_data.get("scores", {})
            current_rank = rank_idx + 1
            
            # Check if score already exists for this vendor
            existing_score = db.query(ScoreModel).filter(
                ScoreModel.vendor_id == vendor_data["id"],
                ScoreModel.rfq_id == rfq_id
            ).first()
            
            if existing_score:
                # Update existing score
                existing_score.price_score = scores.get("price_score")
                existing_score.delivery_score = scores.get("delivery_score")
                existing_score.compliance_score = scores.get("compliance_score")
                existing_score.weighted_score = scores.get("weighted_score")
                existing_score.rank = current_rank
                existing_score.price_justification = scores.get("price_justification")
                existing_score.delivery_justification = scores.get("delivery_justification")
                existing_score.compliance_justification = scores.get("compliance_justification")
                existing_score.overall_justification = scores.get("overall_justification")
            else:
                # Create new score record
                score_record = ScoreModel(
                    id=str(uuid.uuid4()),
                    rfq_id=rfq_id,
                    vendor_id=vendor_data["id"],
                    price_score=scores.get("price_score"),
                    delivery_score=scores.get("delivery_score"),
                    compliance_score=scores.get("compliance_score"),
                    weighted_score=scores.get("weighted_score"),
                    rank=current_rank,
                    price_justification=scores.get("price_justification"),
                    delivery_justification=scores.get("delivery_justification"),
                    compliance_justification=scores.get("compliance_justification"),
                    overall_justification=scores.get("overall_justification"),
                    score_details=scores
                )
                db.add(score_record)
            
            results.append({
                "vendor_id": vendor_data["id"],
                "vendor_name": vendor_data.get("vendor_name"),
                "rank": current_rank,
                "scores": scores
            })
        
        db.commit()
        
        return {
            "message": "Scoring completed successfully",
            "rfq_id": rfq_id,
            "weights": weights,
            "results": results,
            "summary": summary
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Scoring failed: {str(e)}"
        )


@router.get("/{rfq_id}/scores", response_model=list)
def get_scores(rfq_id: str, db: Session = Depends(get_db)):
    """Retrieve all scores for an RFQ, sorted by rank (highest score first)."""
    try:
        scores = db.query(ScoreModel).filter(
            ScoreModel.rfq_id == rfq_id
        ).order_by(ScoreModel.weighted_score.desc()).all()
        
        if not scores:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No scores found for RFQ {rfq_id}"
            )
        
        return scores
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching scores: {str(e)}"
        )


# ==================== Recommendation Endpoints ====================

@router.post("/{rfq_id}/recommend", status_code=status.HTTP_201_CREATED)
def generate_recommendation(rfq_id: str, db: Session = Depends(get_db)):
    """
    Generate vendor ranking and award recommendation.
    
    Requires: Vendors and scores must already exist for the RFQ.
    """
    try:
        # Verify RFQ exists
        rfq = db.query(RFQModel).filter(RFQModel.id == rfq_id).first()
        if not rfq:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"RFQ with ID {rfq_id} not found"
            )
        
        # Fetch vendors with their scores
        vendors = db.query(VendorModel).filter(
            VendorModel.rfq_id == rfq_id
        ).all()
        
        if not vendors:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="No vendors found for this RFQ"
            )
        
        # Get scores for each vendor
        vendor_dicts = []
        for v in vendors:
            score = db.query(ScoreModel).filter(
                ScoreModel.vendor_id == v.id,
                ScoreModel.rfq_id == rfq_id
            ).first()
            
            if not score:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"No scores found for vendor {v.vendor_name}. Run scoring first."
                )
            
            vendor_dicts.append({
                "id": v.id,
                "vendor_name": v.vendor_name,
                "total_cost": v.total_cost,
                "total_cost_usd": v.total_cost_usd,
                "timeline_weeks": v.timeline_weeks,
                "scope_coverage": v.scope_coverage,
                "key_terms": v.key_terms,
                "scores": {
                    "price_score": score.price_score,
                    "delivery_score": score.delivery_score,
                    "compliance_score": score.compliance_score,
                    "weighted_score": score.weighted_score,
                    "price_justification": score.price_justification,
                    "delivery_justification": score.delivery_justification,
                    "compliance_justification": score.compliance_justification,
                    "overall_justification": score.overall_justification
                }
            })
        
        # Generate recommendation
        recommendation = recommend(vendor_dicts, {"id": rfq_id, "project_name": rfq.project_name})
        
        return {
            "message": "Recommendation generated successfully",
            "rfq_id": rfq_id,
            "recommendation": recommendation
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Recommendation generation failed: {str(e)}"
        )


@router.get("/{rfq_id}/results")
def get_analysis_results(rfq_id: str, db: Session = Depends(get_db)):
    """
    Get complete analysis results for an RFQ including scores and recommendation.
    """
    try:
        # Verify RFQ exists
        rfq = db.query(RFQModel).filter(RFQModel.id == rfq_id).first()
        if not rfq:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"RFQ with ID {rfq_id} not found"
            )
        
        # Get all vendors and scores
        vendors = db.query(VendorModel).filter(
            VendorModel.rfq_id == rfq_id
        ).all()
        
        scores = db.query(ScoreModel).filter(
            ScoreModel.rfq_id == rfq_id
        ).order_by(ScoreModel.rank).all()
        
        if not scores:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Scoring has not been run for this RFQ. Run /analysis/{rfq_id}/score first."
            )
        
        # Build results
        results = []
        for score in scores:
            vendor = next((v for v in vendors if v.id == score.vendor_id), None)
            if vendor:
                results.append({
                    "rank": score.rank,
                    "vendor_name": vendor.vendor_name,
                    "vendor_id": vendor.id,
                    "total_cost_usd": vendor.total_cost_usd,
                    "timeline_weeks": vendor.timeline_weeks,
                    "price_score": score.price_score,
                    "delivery_score": score.delivery_score,
                    "compliance_score": score.compliance_score,
                    "weighted_score": score.weighted_score,
                    "justifications": {
                        "price": score.price_justification,
                        "delivery": score.delivery_justification,
                        "compliance": score.compliance_justification,
                        "overall": score.overall_justification
                    }
                })
        
        return {
            "rfq_id": rfq_id,
            "rfq_project_name": rfq.project_name,
            "total_vendors": len(vendors),
            "results": results,
            "best_vendor": results[0] if results else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching results: {str(e)}"
        )
