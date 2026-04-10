from fastapi import APIRouter
from app.schemas.rfq import RFQ
from app.agents.questionnaire_agent import generate_questionnaire

router = APIRouter()

RFQ_STORE = {}

@router.post("/create")
def submit_rfq(rfq: RFQ):
    RFQ_STORE["current"] = rfq
    return {"message": "RFQ stored successfully"}

@router.get("/generate-questions")
def generate_questions():
    rfq = RFQ_STORE.get("current")
    questions = generate_questionnaire(rfq)
    return questions