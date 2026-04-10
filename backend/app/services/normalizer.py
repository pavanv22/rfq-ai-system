def normalize_currency(amount, currency):
    rates = {
        "INR": 0.012,
        "USD": 1
    }
    return float(amount) * rates.get(currency, 1)

def compute_score(data):
    score = 0

    if data["total_cost"]:
        score += 4
    if data["timeline"]:
        score += 3
    if data["scope_coverage"]:
        score += 3

    return score

def normalize(data):
    # Currency normalization
    rates = {"INR": 0.012, "USD": 1}

    if "total_cost" in data and "currency" in data:
        rate = rates.get(data["currency"], 1)
        data["total_cost_usd"] = float(data["total_cost"]) * rate

    return data