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