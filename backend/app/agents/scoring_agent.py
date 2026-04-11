import openai
import json
import re

# Configure to use Ollama API (compatible with OpenAI protocol)
openai.api_base = "http://localhost:11434/v1"
openai.api_key = "not-needed"


def clean_json(text):
    """
    Extract and clean JSON from response text.
    Handles markdown, extra text, and formatting issues.
    """
    if not text:
        return None
    
    # Remove markdown code blocks
    text = text.replace("```json", "").replace("```", "").strip()
    
    # Try to extract JSON object (most common case)
    # Find the first { and the last }
    start_idx = text.find('{')
    end_idx = text.rfind('}')
    
    if start_idx >= 0 and end_idx > start_idx:
        json_str = text[start_idx:end_idx+1]
        
        # Clean up common JSON issues
        # Fix missing commas between after } before another key
        json_str = re.sub(r'"\s*}(\s*)"', '"},"', json_str)
        # Fix single quotes to double quotes in keys
        json_str = re.sub(r"'([^']*)':", r'"\1":', json_str)
        
        return json_str
    
    return None


def fallback_score_from_data(vendor_data, scoring_weights=None):
    """
    Generate scores based on vendor data directly (when AI fails).
    Uses heuristics to score price, delivery, and compliance.
    Handles None/missing values gracefully.
    
    Args:
        vendor_data: Dict containing vendor information
        scoring_weights: Optional dict with scoring weights (default 0.4, 0.3, 0.3)
    
    Returns:
        Dict with scores and justifications
    """
    if scoring_weights is None:
        scoring_weights = {
            "price_weight": 0.4,
            "delivery_weight": 0.3,
            "compliance_weight": 0.3
        }
    
    price_score = 7  # Default good score
    delivery_score = 7
    compliance_score = 7
    
    # Price scoring based on cost - handle None values
    cost = vendor_data.get("total_cost_usd") or 0
    if cost and cost > 0:
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
    
    # Delivery scoring based on timeline - handle None values
    timeline = vendor_data.get("timeline_weeks") or 4
    # Ensure timeline is numeric
    try:
        timeline = int(timeline) if timeline else 4
    except (ValueError, TypeError):
        timeline = 4
    
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
    
    # Compliance scoring based on scope coverage - handle None values
    scope = vendor_data.get("scope_coverage") or []
    if isinstance(scope, list):
        scope_count = len(scope)
    else:
        scope_count = 0
    
    # Assume max 5 scope items for scoring
    if scope_count > 0:
        scope_coverage_percent = (scope_count / 5.0) * 10
    else:
        scope_coverage_percent = 5  # Minimal score if no scope info
    
    compliance_score = min(10, max(3, int(scope_coverage_percent)))
    
    # Format cost for display
    cost_str = f"${cost:,.2f}" if cost > 0 else "Not specified"
    timeline_str = f"{timeline}" if timeline else "Not specified"
    
    # Calculate weighted score
    weighted_score = (
        price_score * scoring_weights["price_weight"] +
        delivery_score * scoring_weights["delivery_weight"] +
        compliance_score * scoring_weights["compliance_weight"]
    ) * 10  # Scale to 0-100
    
    return {
        "price_score": int(price_score),
        "price_justification": f"Cost estimate: {cost_str}",
        "delivery_score": int(delivery_score),
        "delivery_justification": f"Timeline: {timeline_str} weeks",
        "compliance_score": int(compliance_score),
        "compliance_justification": f"Scope coverage: {scope_count} items covered",
        "overall_justification": f"Estimated score based on provided data (fallback scoring)",
        "weighted_score": round(weighted_score, 2)
    }


def score_vendor(vendor_data, scoring_weights=None, timeout=30):
    """
    Score a vendor based on multiple criteria using Ollama/Llama3 API.
    
    Args:
        vendor_data: Dict containing vendor information
        scoring_weights: Dict with keys (price_weight, delivery_weight, compliance_weight)
                        Defaults to 0.4, 0.3, 0.3 if not provided
        timeout: Timeout in seconds for LLM request (default 30)
    
    Returns:
        Dict with individual scores, weighted total, and justifications
    """
    if scoring_weights is None:
        scoring_weights = {
            "price_weight": 0.4,
            "delivery_weight": 0.3,
            "compliance_weight": 0.3
        }
    
    prompt = f"""You are a procurement expert evaluating vendor quotations.

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
- Vendor Name: {vendor_data.get('vendor_name', 'Unknown')}
- Cost: ${vendor_data.get('total_cost_usd', 'N/A')} USD
- Timeline: {vendor_data.get('timeline_weeks', 'N/A')} weeks
- Scope Coverage: {vendor_data.get('scope_coverage', 'Not specified')}
- Key Terms: {vendor_data.get('key_terms', 'Not specified')}

IMPORTANT: You MUST respond with ONLY a valid JSON object, nothing else.
Use this exact format with no markdown or extra text:
{{"price_score": 7, "price_justification": "brief reason", "delivery_score": 7, "delivery_justification": "brief reason", "compliance_score": 7, "compliance_justification": "brief reason", "overall_justification": "summary"}}

Remember: Return ONLY the JSON object. No markdown. No extra text."""

    try:
        response = openai.ChatCompletion.create(
            model="llama3:latest",
            messages=[
                {"role": "user", "content": prompt}
            ],
            timeout=timeout,
            temperature=0.5  # Lower temperature for more consistent outputs
        )
        
        # Extract and clean the response
        response_text = response["choices"][0]["message"]["content"]
        cleaned_text = clean_json(response_text)
        
        if not cleaned_text:
            print("Warning: Could not extract JSON from response, using fallback")
            return fallback_score_from_data(vendor_data, scoring_weights)
        
        result = json.loads(cleaned_text)
        
        # Ensure all required fields exist
        required_fields = ["price_score", "delivery_score", "compliance_score"]
        if not all(k in result for k in required_fields):
            print("Warning: AI response missing required fields, using fallback")
            return fallback_score_from_data(vendor_data, scoring_weights)
        
        # Ensure scores are integers and valid (1-10)
        try:
            price_score = int(result.get("price_score", 5))
            delivery_score = int(result.get("delivery_score", 5))
            compliance_score = int(result.get("compliance_score", 5))
        except (ValueError, TypeError):
            print("Warning: Invalid score format from AI, using fallback")
            return fallback_score_from_data(vendor_data, scoring_weights)
        
        # Validate score ranges
        price_score = max(1, min(10, price_score))
        delivery_score = max(1, min(10, delivery_score))
        compliance_score = max(1, min(10, compliance_score))
        
        weighted_score = (
            price_score * scoring_weights["price_weight"] +
            delivery_score * scoring_weights["delivery_weight"] +
            compliance_score * scoring_weights["compliance_weight"]
        ) * 10  # Scale to 0-100
        
        result["price_score"] = price_score
        result["delivery_score"] = delivery_score
        result["compliance_score"] = compliance_score
        result["weighted_score"] = round(weighted_score, 2)
        
        return result
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing error from Ollama: {e}. Using fallback scoring.")
        result = fallback_score_from_data(vendor_data, scoring_weights)
    except Exception as e:
        print(f"Error scoring vendor with AI: {e}. Using fallback scoring.")
        result = fallback_score_from_data(vendor_data, scoring_weights)
    
    # Return the fallback result (already has weighted_score calculated)
    return result
