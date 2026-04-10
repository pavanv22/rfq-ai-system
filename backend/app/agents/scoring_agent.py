import openai
import json
import re

# Configure to use Ollama API (compatible with OpenAI protocol)
openai.api_base = "http://localhost:11434/v1"
openai.api_key = "not-needed"


def clean_json(text):
    """Remove markdown code blocks from JSON strings."""
    text = text.replace("```json", "").replace("```", "").strip()
    # Try to extract JSON if there's text before/after it
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        return match.group(0)
    return text


def fallback_score_from_data(vendor_data):
    """
    Generate scores based on vendor data directly (when AI fails).
    Uses heuristics to score price, delivery, and compliance.
    """
    price_score = 7  # Default good score
    delivery_score = 7
    compliance_score = 7
    
    # Price scoring based on cost
    cost = vendor_data.get("total_cost_usd", 0)
    if cost:
        # Higher cost = lower price score (inverse relationship)
        # Assume good price is under $50k, great is under $20k
        if cost < 20000:
            price_score = 9
        elif cost < 35000:
            price_score = 8
        elif cost < 50000:
            price_score = 7
        elif cost < 75000:
            price_score = 6
        else:
            price_score = 5
    
    # Delivery scoring based on timeline
    timeline = vendor_data.get("timeline_weeks", 4)
    if timeline <= 2:
        delivery_score = 9
    elif timeline <= 4:
        delivery_score = 8
    elif timeline <= 8:
        delivery_score = 7
    elif timeline <= 12:
        delivery_score = 6
    else:
        delivery_score = 5
    
    # Compliance scoring based on scope coverage
    scope = vendor_data.get("scope_coverage", [])
    scope_coverage_percent = len(scope) / max(1, 5) * 10  # Assuming max 5 scope items
    compliance_score = min(10, max(5, scope_coverage_percent))
    
    return {
        "price_score": int(price_score),
        "price_justification": f"Cost estimate: ${cost:,.2f}",
        "delivery_score": int(delivery_score),
        "delivery_justification": f"Timeline: {timeline} weeks",
        "compliance_score": int(compliance_score),
        "compliance_justification": f"Scope coverage: {len(scope)} items",
        "overall_justification": f"Estimated score based on provided data"
    }


def score_vendor(vendor_data, scoring_weights=None):
    """
    Score a vendor based on multiple criteria using Ollama/Llama3 API.
    
    Args:
        vendor_data: Dict containing vendor information
        scoring_weights: Dict with keys (price_weight, delivery_weight, compliance_weight)
                        Defaults to 0.4, 0.3, 0.3 if not provided
    
    Returns:
        Dict with individual scores, weighted score, and justifications
    """
    if scoring_weights is None:
        scoring_weights = {
            "price_weight": 0.4,
            "delivery_weight": 0.3,
            "compliance_weight": 0.3
        }
    
    prompt = f"""
You are a procurement expert evaluating vendor quotations.

Evaluate this vendor on THREE criteria, each on a scale of 1-10:

1. PRICE COMPETITIVENESS (Score 1-10)
   - Is the quoted price reasonable?
   - Does it offer good value?
   
2. DELIVERY TIMELINE (Score 1-10)
   - Can the vendor meet our timeline?
   - Is the delivery timeline realistic?
   
3. COMPLIANCE & TERMS (Score 1-10)
   - Are vendor terms acceptable?
   - Any compliance issues?
   - Is the scope coverage adequate?

Vendor Data:
{json.dumps(vendor_data, indent=2)}

You MUST respond ONLY with valid JSON in this exact format:
{{
    "price_score": number from 1 to 10,
    "price_justification": "brief explanation",
    "delivery_score": number from 1 to 10,
    "delivery_justification": "brief explanation",
    "compliance_score": number from 1 to 10,
    "compliance_justification": "brief explanation",
    "overall_justification": "brief summary"
}}

DO NOT include any text outside the JSON. Do not include markdown formatting.
"""

    try:
        response = openai.ChatCompletion.create(
            model="tinyllama:latest",
            messages=[
                {"role": "user", "content": prompt}
            ],
            timeout=60
        )
        
        # Extract and clean the response
        response_text = response["choices"][0]["message"]["content"]
        cleaned_text = clean_json(response_text)
        result = json.loads(cleaned_text)
        
        # Ensure all required fields exist
        if not all(k in result for k in ["price_score", "delivery_score", "compliance_score"]):
            print("Warning: AI response missing required fields, using fallback")
            result = fallback_score_from_data(vendor_data)
        
        # Calculate weighted score
        price_score = result.get("price_score", 5)
        delivery_score = result.get("delivery_score", 5)
        compliance_score = result.get("compliance_score", 5)
        
        weighted_score = (
            price_score * scoring_weights["price_weight"] +
            delivery_score * scoring_weights["delivery_weight"] +
            compliance_score * scoring_weights["compliance_weight"]
        ) * 10  # Scale to 0-100
        
        result["weighted_score"] = round(weighted_score, 2)
        
        return result
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing error from Ollama: {e}. Using fallback scoring.")
        result = fallback_score_from_data(vendor_data)
    except Exception as e:
        print(f"Error scoring vendor with AI: {e}. Using fallback scoring.")
        result = fallback_score_from_data(vendor_data)
    
    # Calculate weighted score for fallback
    price_score = result.get("price_score", 5)
    delivery_score = result.get("delivery_score", 5)
    compliance_score = result.get("compliance_score", 5)
    
    weighted_score = (
        price_score * scoring_weights["price_weight"] +
        delivery_score * scoring_weights["delivery_weight"] +
        compliance_score * scoring_weights["compliance_weight"]
    ) * 10  # Scale to 0-100
    
    result["weighted_score"] = round(weighted_score, 2)
    
    return result
