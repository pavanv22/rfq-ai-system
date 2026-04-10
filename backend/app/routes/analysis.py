# from fastapi import APIRouter
# from app.services.scoring import compute_score
# from app.agents.decision_agent import recommend

# router = APIRouter()

# # TEMP in-memory store (we will replace later with DB)
# VENDOR_DATA = [
#     {
#         "name": "Vendor A",
#         "total_cost": 100000,
#         "timeline": 4,
#         "scope_coverage": ["video production", "editing"],
#         "compliance_score": 8
#     },
#     {
#         "name": "Vendor B",
#         "total_cost": 80000,
#         "timeline": 6,
#         "scope_coverage": ["video production"],
#         "compliance_score": 6
#     }
# ]


# @router.get("/run")
# def run_analysis():
#     results = []

#     for vendor in VENDOR_DATA:
#         score = compute_score(vendor)
#         vendor["score"] = score
#         results.append(vendor)

#     decision = recommend(results)

#     return {
#         "vendors": results,
#         "recommendation": decision
#     }


from fastapi import APIRouter
from fastapi import HTTPException
from app.services.storage import load_vendor_data
from app.services.scoring import compute_score
from app.agents.decision_agent import recommend

router = APIRouter()

# @router.get("/run")
# def run_analysis():
#     vendors = load_vendor_data()

#     results = []

#     for vendor in vendors:
#         score = compute_score(vendor)
#         vendor["score"] = score
#         results.append(vendor)
#     print("DEBUG - Results:", results)
#     decision = recommend(results)

#     return {
#         "vendors": results,
#         "recommendation": decision
#     }

@router.get("/run")
def run_analysis():
    try:
        vendors = load_vendor_data()
        results = compute_score(vendors)
        decision = recommend(results)

        return {
            "results": results,
            "decision": decision
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))