import openai
import json
import re
openai.api_base = "http://localhost:11434/v1"
openai.api_key = "not-needed"

def clean_json(text):
    return text.replace("```json", "").replace("```", "").strip()  

def fallback_extraction(raw_text):
    """Fallback regex-based extraction when AI fails"""
    try:
        lines = raw_text.split('\n')
        data = {
            "vendor_name": "Unknown Vendor",
            "total_cost": None,
            "currency": "USD",
            "timeline_weeks": 4,
            "scope_coverage": [],
            "key_terms": []
        }
        
        # Try to extract vendor name from first lines
        for line in lines[:10]:
            if "vendor:" in line.lower() or "company:" in line.lower():
                data["vendor_name"] = line.split(":", 1)[1].strip()
                break
        
        # Try to find cost - check for various currency patterns
        for line in lines:
            # USD: $45,000 or $45000
            match = re.search(r'\$[\d,]+(?:\.\d{2})?', line)
            if match:
                cost_str = match.group(0).replace("$", "").replace(",", "")
                data["total_cost"] = float(cost_str)
                data["currency"] = "USD"
                break
            
            # EUR: €42,000
            match = re.search(r'€[\d,]+(?:\.\d{2})?', line)
            if match:
                cost_str = match.group(0).replace("€", "").replace(",", "")
                data["total_cost"] = float(cost_str)
                data["currency"] = "EUR"
                break
            
            # GBP: £13,300
            match = re.search(r'£[\d,]+(?:\.\d{2})?', line)
            if match:
                cost_str = match.group(0).replace("£", "").replace(",", "")
                data["total_cost"] = float(cost_str)
                data["currency"] = "GBP"
                break
            
            # INR: ₹3,600,000
            match = re.search(r'₹[\d,]+(?:\.\d{2})?', line)
            if match:
                cost_str = match.group(0).replace("₹", "").replace(",", "")
                data["total_cost"] = float(cost_str)
                data["currency"] = "INR"
                break
            
            # Generic: numbers with 3+ digits followed by currency code
            match = re.search(r'([\d,]+(?:\.\d{2})?)\s*(USD|EUR|GBP|INR|AUD|CAD)', line, re.IGNORECASE)
            if match and not data["total_cost"]:
                cost_str = match.group(1).replace(",", "")
                try:
                    data["total_cost"] = float(cost_str)
                    data["currency"] = match.group(2).upper()
                except:
                    pass
        
        # Try to extract timeline
        timeline_match = re.search(r'(\d+)\s*(week|day|month)', raw_text, re.IGNORECASE)
        if timeline_match:
            num = int(timeline_match.group(1))
            unit = timeline_match.group(2).lower()
            if "day" in unit:
                data["timeline_weeks"] = max(1, num // 7)
            elif "month" in unit:
                data["timeline_weeks"] = num * 4
            else:
                data["timeline_weeks"] = num
        
        return data
    except Exception as e:
        print(f"Fallback extraction error: {e}")
        return {"error": f"Fallback extraction failed: {str(e)}"}

def extract_structured_data(raw_text):
    """Extract structured data using AI with fallback"""
    try:
        # Try with lighter tinyllama model first
        response = openai.ChatCompletion.create(
            model="tinyllama:latest",
            messages=[
                {
                    "role": "user", 
                    "content": f"""Extract vendor info as JSON only:
Fields: vendor_name, total_cost (number), currency, timeline_weeks (number), scope_coverage (list), key_terms (list)

TEXT:
{raw_text[:2000]}"""
                }
            ],
            timeout=30
        )
        result = json.loads(clean_json(response["choices"][0]["message"]["content"]))
        return result
    except Exception as e:
        print(f"AI extraction failed ({type(e).__name__}), using fallback: {e}")
        # Fallback to regex extraction
        return fallback_extraction(raw_text)