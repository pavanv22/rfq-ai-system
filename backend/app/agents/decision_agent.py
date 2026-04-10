def recommend(vendors):
    best = max(vendors, key=lambda x: x["score"])
    return {
        "winner": best["name"],
        "reason": "Highest combined score"
    }