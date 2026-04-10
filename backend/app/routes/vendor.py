from fastapi import APIRouter, UploadFile, File
import shutil
import os

from app.services.extractor import extract_text
from app.agents.extraction_agent import extract_structured_data
from app.services.normalizer import normalize
from app.services.storage import save_vendor_data

router = APIRouter()

UPLOAD_DIR = "data/uploads"

# @router.post("/upload")
# async def upload_file(file: UploadFile = File(...)):
#     # Step 0: Save file
#     file_path = os.path.join(UPLOAD_DIR, file.filename)

#     with open(file_path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)

#     # Step 1: Extract raw text
#     raw_text = extract_text(file_path)

#     # Step 2: AI structured extraction
#     structured_data = extract_structured_data(raw_text)

#     # Step 3: Normalize data
#     structured_data = normalize(structured_data)

#     # Step 4: Save to storage
#     save_vendor_data(structured_data)

#     return {
#         "message": "File processed successfully",
#         "structured_data": structured_data
#     }

# Ensure directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Step 0: Save file
        file_path = os.path.join(UPLOAD_DIR, file.filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Step 1: Extract raw text
        raw_text = extract_text(file_path)

        if not raw_text:
            return {"error": "Text extraction failed"}

        # Step 2: AI structured extraction
        structured_data = extract_structured_data(raw_text)

        if "error" in structured_data:
            return {
                "error": "LLM extraction failed",
                "raw_output": structured_data.get("raw")
            }

        # Step 3: Normalize data
        structured_data = normalize(structured_data)

        # Step 4: Add metadata (VERY IMPORTANT)
        structured_data["source_file"] = file.filename
        structured_data["raw_text"] = raw_text[:500]  # store partial for debugging

        # Step 5: Save to storage
        save_vendor_data(structured_data)

        return {
            "message": "File processed successfully",
            "structured_data": structured_data
        }

    except Exception as e:
        return {
            "error": "Upload pipeline failed",
            "details": str(e)
        }