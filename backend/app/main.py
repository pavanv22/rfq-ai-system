from fastapi import FastAPI
from app.routes import rfq, vendor, analysis
from app.models import init_db

app = FastAPI(title="RFQ AI System")

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()
    print("Database initialized successfully")

@app.get("/")
def root():
    return {"message": "RFQ AI System API running"}

app.include_router(rfq.router, prefix="/rfq")
app.include_router(vendor.router, prefix="/vendor")
app.include_router(analysis.router, prefix="/analysis")