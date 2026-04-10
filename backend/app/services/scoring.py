# def compute_score(data):
#     score = 0

#     # Cost (lower is better)
#     if data.get("total_cost"):
#         if data["total_cost"] < 90000:
#             score += 4
#         else:
#             score += 2

#     # Timeline (shorter is better)
#     if data.get("timeline"):
#         if data["timeline"] <= 4:
#             score += 3
#         else:
#             score += 1

#     # Scope coverage
#     if data.get("scope_coverage"):
#         score += min(len(data["scope_coverage"]), 3)

#     # Compliance (AI-driven)
#     score += data.get("compliance_score", 0) * 0.5

#     return round(score, 2)

from app.agents.scoring_agent import score_vendor

def score_vendors(vendors):
    results = []

    for v in vendors:
        ai_score = score_vendor(v)

        v["score"] = ai_score["score"]
        v["justification"] = ai_score["justification"]

        results.append(v)

    return results