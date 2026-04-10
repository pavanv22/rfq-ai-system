def recommend(vendors):
    if not vendors:
        return {
            "message": "No vendor data available. Please upload vendor files first.",
            "best_vendor": None
        }

    best = max(vendors, key=lambda x: x.get("score", 0))

    return {
        "best_vendor": best,
        "message": "Recommendation generated successfully"
    }