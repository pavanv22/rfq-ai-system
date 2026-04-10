from fastapi import FastAPI
from app.routes import rfq, vendor, analysis

app = FastAPI(title="RFQ AI System")

app.include_router(rfq.router, prefix="/rfq")
app.include_router(vendor.router, prefix="/vendor")
app.include_router(analysis.router, prefix="/analysis")