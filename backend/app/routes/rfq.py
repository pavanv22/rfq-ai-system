from fastapi import APIRouter
from app.schemas.rfq import RFQ
from app.agents.questionnaire_agent import generate_questionnaire

router = APIRouter()

RFQ_DB = {}

@router.post("/create")
def create_rfq(rfq: RFQ):
    RFQ_DB["current"] = rfq
    return {"message": "RFQ stored successfully"}

@router.get("/generate-questions")
def generate_questions():
    rfq = RFQ_DB.get("current")
    questions = generate_questionnaire(rfq)
    return questions