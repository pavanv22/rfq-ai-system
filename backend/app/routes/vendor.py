from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import shutil
import os
import uuid

from app.models import (
    VendorModel, VendorCreate, VendorUpdate, VendorResponse,
    RFQModel, get_db
)
from app.services.extractor import extract_text
from app.agents.extraction_agent import extract_structured_data
from app.services.normalizer import normalize, detect_missing_fields, infer_missing_values
from app.services.storage import save_vendor_data

router = APIRouter(tags=["Vendor"])

UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ==================== Vendor CRUD Endpoints ====================

@router.post("/", response_model=VendorResponse, status_code=status.HTTP_201_CREATED)
def create_vendor(vendor_data: VendorCreate, db: Session = Depends(get_db)):
    """Create a new vendor entry."""
    try:
        # Verify RFQ exists
        rfq = db.query(RFQModel).filter(RFQModel.id == vendor_data.rfq_id).first()
        if not rfq:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"RFQ with ID {vendor_data.rfq_id} not found"
            )
        
        vendor = VendorModel(
            id=str(uuid.uuid4()),
            **vendor_data.dict()
        )
        db.add(vendor)
        db.commit()
        db.refresh(vendor)
        return vendor
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating vendor: {str(e)}"
        )


@router.get("/rfq/{rfq_id}", response_model=List[VendorResponse])
def list_vendors_by_rfq(rfq_id: str, db: Session = Depends(get_db)):
    """List all vendors for a specific RFQ."""
    try:
        # Verify RFQ exists
        rfq = db.query(RFQModel).filter(RFQModel.id == rfq_id).first()
        if not rfq:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"RFQ with ID {rfq_id} not found"
            )
        
        vendors = db.query(VendorModel).filter(
            VendorModel.rfq_id == rfq_id
        ).all()
        return vendors
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching vendors: {str(e)}"
        )


@router.get("/{vendor_id}", response_model=VendorResponse)
def get_vendor(vendor_id: str, db: Session = Depends(get_db)):
    """Get a single vendor by ID."""
    try:
        vendor = db.query(VendorModel).filter(VendorModel.id == vendor_id).first()
        if not vendor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vendor with ID {vendor_id} not found"
            )
        return vendor
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching vendor: {str(e)}"
        )


@router.put("/{vendor_id}", response_model=VendorResponse)
def update_vendor(vendor_id: str, vendor_data: VendorUpdate, db: Session = Depends(get_db)):
    """Update vendor information."""
    try:
        vendor = db.query(VendorModel).filter(VendorModel.id == vendor_id).first()
        if not vendor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vendor with ID {vendor_id} not found"
            )
        
        update_data = vendor_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(vendor, field, value)
        
        db.commit()
        db.refresh(vendor)
        return vendor
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating vendor: {str(e)}"
        )


@router.delete("/{vendor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vendor(vendor_id: str, db: Session = Depends(get_db)):
    """Delete a vendor."""
    try:
        vendor = db.query(VendorModel).filter(VendorModel.id == vendor_id).first()
        if not vendor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vendor with ID {vendor_id} not found"
            )
        
        db.delete(vendor)
        db.commit()
        return None
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting vendor: {str(e)}"
        )


# ==================== File Upload & Processing ====================

@router.post("/{rfq_id}/upload", status_code=status.HTTP_201_CREATED)
async def upload_vendor_file(
    rfq_id: str,
    file: UploadFile = File(...),
    vendor_name: str = None,
    db: Session = Depends(get_db)
):
    """
    Upload and process a vendor quotation file.
    
    Supported formats: PDF, DOCX, PPTX, XLSX, PNG, JPG
    
    Pipeline:
    1. Save file to disk
    2. Extract text (based on file type)
    3. AI extraction of structured data
    4. Normalization (currency conversion, missing field detection)
    5. Store in database
    """
    try:
        # Step 1: Verify RFQ exists
        rfq = db.query(RFQModel).filter(RFQModel.id == rfq_id).first()
        if not rfq:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"RFQ with ID {rfq_id} not found"
            )
        
        # Step 2: Save file with UUID prefix to avoid collisions
        file_ext = os.path.splitext(file.filename)[1]
        unique_filename = f"{str(uuid.uuid4())}{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Step 3: Extract raw text
        raw_text = extract_text(file_path)
        print(f"[UPLOAD DEBUG] Raw text extracted: {len(raw_text) if raw_text else 0} chars")
        if not raw_text:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Failed to extract text from file"
            )
        
        # Show first 500 chars for debugging
        print(f"[UPLOAD DEBUG] Text preview: {raw_text[:500]}")
        
        # Step 4: AI structured extraction
        structured_data = extract_structured_data(raw_text)
        print(f"[UPLOAD DEBUG] Structured data: {structured_data}")
        
        if "error" in structured_data:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"LLM extraction failed: {structured_data.get('error')}"
            )
        
        # Step 5: Detect missing fields
        missing_fields = detect_missing_fields(structured_data)
        
        # Step 6: Attempt to infer missing values using AI
        ai_inferred = False
        if missing_fields:
            inferred_data = infer_missing_values(raw_text, structured_data, missing_fields)
            if inferred_data:
                structured_data.update(inferred_data)
                ai_inferred = True
                missing_fields = [f for f in missing_fields if f not in inferred_data]
        
        # Step 7: Normalize data (currency conversion, etc.)
        normalized_data = normalize(structured_data)
        
        # Step 8: Use provided vendor_name or use extracted name
        vendor_name_final = vendor_name or structured_data.get("vendor_name", f"Vendor_{unique_filename}")
        
        # Step 9: Check if vendor with same name already exists for this RFQ (UPDATE instead of CREATE)
        existing_vendor = db.query(VendorModel).filter(
            VendorModel.rfq_id == rfq_id,
            VendorModel.vendor_name == vendor_name_final
        ).first()
        
        if existing_vendor:
            # UPDATE existing vendor with new data
            print(f"[UPLOAD DEBUG] Updating existing vendor: {vendor_name_final}")
            existing_vendor.total_cost = structured_data.get("total_cost")
            existing_vendor.currency = structured_data.get("currency", "USD")
            existing_vendor.total_cost_usd = normalized_data.get("total_cost_usd")
            existing_vendor.timeline_weeks = structured_data.get("timeline_weeks")
            existing_vendor.scope_coverage = structured_data.get("scope_coverage")
            existing_vendor.key_terms = structured_data.get("key_terms")
            existing_vendor.raw_extracted_data = structured_data
            existing_vendor.normalized_data = normalized_data
            existing_vendor.extraction_status = "normalized" if not missing_fields else "incomplete"
            existing_vendor.missing_fields = missing_fields if missing_fields else None
            existing_vendor.ai_inferred_fields = ai_inferred
            existing_vendor.file_path = file_path
            existing_vendor.file_type = file.content_type or file_ext
            
            db.commit()
            db.refresh(existing_vendor)
            vendor = existing_vendor
        else:
            # CREATE new vendor (original behavior)
            print(f"[UPLOAD DEBUG] Creating new vendor: {vendor_name_final}")
            vendor = VendorModel(
                id=str(uuid.uuid4()),
                rfq_id=rfq_id,
                vendor_name=vendor_name_final,
                total_cost=structured_data.get("total_cost"),
                currency=structured_data.get("currency", "USD"),
                total_cost_usd=normalized_data.get("total_cost_usd"),
                currency_normalized="USD",
                timeline_weeks=structured_data.get("timeline_weeks"),
                scope_coverage=structured_data.get("scope_coverage"),
                key_terms=structured_data.get("key_terms"),
                raw_extracted_data=structured_data,
                normalized_data=normalized_data,
                extraction_status="normalized" if not missing_fields else "incomplete",
                missing_fields=missing_fields if missing_fields else None,
                ai_inferred_fields=ai_inferred,
                file_path=file_path,
                file_type=file.content_type or file_ext
            )
            
            db.add(vendor)
            db.commit()
            db.refresh(vendor)
        
        # Step 10: Save to legacy storage (for backward compatibility)
        save_vendor_data(normalized_data)
        
        return {
            "message": "File processed successfully",
            "vendor_id": vendor.id,
            "vendor_name": vendor_name_final,
            "extraction_status": vendor.extraction_status,
            "missing_fields": missing_fields,
            "ai_inferred_fields": ai_inferred,
            "structured_data": structured_data,
            "normalized_data": normalized_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload pipeline failed: {str(e)}"
        )
