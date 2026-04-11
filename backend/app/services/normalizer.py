import json
import openai
from typing import Dict, List, Optional

# Configure OpenAI client for Ollama
openai.api_base = "http://localhost:11434/v1"
openai.api_key = "not-needed"

# Currency conversion rates to USD (example rates - update as needed)
CURRENCY_RATES = {
    "USD": 1.0,
    "EUR": 1.08,
    "GBP": 1.27,
    "INR": 0.012,  # 1 INR ≈ 0.012 USD
    "JPY": 0.0067,
    "AUD": 0.66,
    "CAD": 0.74,
    "SGD": 0.74,
    "CNY": 0.14,
    "AED": 0.27,
    "SAR": 0.27,
}

# Required fields for vendor data
REQUIRED_FIELDS = [
    "vendor_name",
    "total_cost",
    "currency",
    "timeline_weeks",
    "scope_coverage",
    "key_terms"
]


def normalize_currency(amount: float, currency: str) -> float:
    """
    Convert amount from given currency to USD.
    
    Args:
        amount: The amount in the specified currency
        currency: The currency code (e.g., "INR", "USD")
    
    Returns:
        Amount in USD
    """
    if not isinstance(amount, (int, float)):
        return 0.0
    
    rate = CURRENCY_RATES.get(currency.upper(), 1.0)
    return float(amount) * rate


def detect_missing_fields(data: Dict) -> List[str]:
    """
    Detect which required fields are missing or have null/empty values.
    
    Args:
        data: Vendor data dictionary
    
    Returns:
        List of missing field names
    """
    missing = []
    for field in REQUIRED_FIELDS:
        value = data.get(field)
        if value is None or value == "" or (isinstance(value, list) and len(value) == 0):
            missing.append(field)
    return missing


def infer_missing_values(
    raw_text: str,
    structured_data: Dict,
    missing_fields: List[str]
) -> Optional[Dict]:
    """
    Use AI to infer missing values from the raw extracted text.
    
    Args:
        raw_text: Raw extracted text from the vendor file
        structured_data: Already extracted structured data
        missing_fields: List of fields that are missing
    
    Returns:
        Dictionary with inferred values for missing fields, or None if inference fails
    """
    if not missing_fields:
        return {}
    
    fields_str = ", ".join(missing_fields)
    
    prompt = f"""
You are analyzing a vendor quotation. Some fields could not be extracted properly.
Using the raw text provided, try to infer the missing fields.

Raw Text:
{raw_text[:2000]}

Already Extracted Data:
{json.dumps(structured_data, indent=2)}

Missing Fields to Infer: {fields_str}

Return a JSON object with the inferred values for ONLY the missing fields.
If you cannot reliably infer a field, do NOT include it in the response.

Example response format:
{{
    "vendor_name": "Acme Corp",
    "timeline_weeks": 4
}}

Return ONLY valid JSON, no other text.
"""
    
    try:
        response = openai.ChatCompletion.create(
            model="llama3:latest",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        response_text = response["choices"][0]["message"]["content"]
        cleaned_text = response_text.replace("```json", "").replace("```", "").strip()
        inferred = json.loads(cleaned_text)
        
        return inferred
    except Exception as e:
        print(f"Warning: Failed to infer missing values: {e}")
        return {}


def normalize(data: Dict) -> Dict:
    """
    Normalize vendor data.
    
    Operations:
    1. Currency conversion to USD
    2. Field cleanup and standardization
    3. Data validation
    
    Args:
        data: Vendor data dictionary
    
    Returns:
        Normalized data dictionary
    """
    normalized = data.copy()
    
    # Currency normalization
    if "total_cost" in normalized and "currency" in normalized:
        try:
            amount = float(normalized["total_cost"])
            currency = str(normalized["currency"]).upper()
            normalized["total_cost_usd"] = round(normalize_currency(amount, currency), 2)
        except (ValueError, TypeError) as e:
            print(f"Warning: Failed to normalize currency: {e}")
            normalized["total_cost_usd"] = 0.0
    
    # Timeline normalization (ensure it's an integer)
    if "timeline_weeks" in normalized:
        try:
            normalized["timeline_weeks"] = int(normalized["timeline_weeks"])
        except (ValueError, TypeError):
            normalized["timeline_weeks"] = None
    
    # Ensure lists are proper lists
    if "scope_coverage" in normalized:
        if isinstance(normalized["scope_coverage"], str):
            try:
                normalized["scope_coverage"] = json.loads(normalized["scope_coverage"])
            except:
                normalized["scope_coverage"] = [normalized["scope_coverage"]]
        elif not isinstance(normalized["scope_coverage"], list):
            normalized["scope_coverage"] = []
    
    if "key_terms" in normalized:
        if isinstance(normalized["key_terms"], str):
            try:
                normalized["key_terms"] = json.loads(normalized["key_terms"])
            except:
                normalized["key_terms"] = [normalized["key_terms"]]
        elif not isinstance(normalized["key_terms"], list):
            normalized["key_terms"] = []
    
    # Ensure vendor_name is a string
    if "vendor_name" in normalized:
        normalized["vendor_name"] = str(normalized["vendor_name"]).strip()
    
    return normalized


def compute_score(data: Dict) -> Dict:
    """
    Compute a basic completeness score for vendor data.
    
    Args:
        data: Vendor data dictionary
    
    Returns:
        Score information dictionary
    """
    score = 0
    max_score = 10
    
    if data.get("total_cost"):
        score += 3
    if data.get("timeline_weeks"):
        score += 3
    if data.get("scope_coverage"):
        score += 2
    if data.get("key_terms"):
        score += 2
    
    return {
        "completeness_score": min(score, max_score),
        "fields_present": sum(1 for f in REQUIRED_FIELDS if data.get(f)),
        "fields_total": len(REQUIRED_FIELDS)
    }
