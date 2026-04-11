# import google.generativeai as genai
# import os
# from dotenv import load_dotenv

# load_dotenv()

# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# print("DEBUG - Gemini API Key Loaded:", os.getenv("GEMINI_API_KEY") is not None)


# def generate_questionnaire(rfq):
#     model = genai.GenerativeModel("gemini-2.5-pro")

#     prompt = f"""
#     RFQ:
#     Scope: {rfq.scope}
#     Timelines: {rfq.timelines}
#     Line Items: {rfq.line_items}   

#     Generate structured vendor questions in JSON:
#     {{
#       "compliance": [],
#       "experience": [],
#       "timeline": [],
#       "pricing": []
#     }}
#     """

#     response = model.generate_content(prompt)
#     return response.text

import requests
import json

OLLAMA_API_URL = "http://localhost:11434/api/generate"
# MODEL = "tinyllama:latest"
MODEL = "llama3:latest"  # Updated model name

def clean_json(text):
    return text.replace("```json", "").replace("```", "").strip()  


def _get_field(src, field_name, default=""):
    """Helper to get field value from dict or object and normalize to string."""
    # dict-like
    try:
        if isinstance(src, dict):
            val = src.get(field_name, default)
        else:
            val = getattr(src, field_name, default)
    except Exception:
        val = default

    # If value is list/dict, convert to readable string
    if isinstance(val, (list, dict)):
        try:
            return json.dumps(val)
        except Exception:
            return str(val)
    return str(val)


def generate_questionnaire(rfq):
    print("DEBUG - Generating questionnaire with RFQ:", getattr(rfq, 'id', None) or (rfq.get('id') if isinstance(rfq, dict) else None))
    
    subject = _get_field(rfq, 'project_name') or _get_field(rfq, 'subject')
    scope = _get_field(rfq, 'scope')
    sourcing = _get_field(rfq, 'sourcing_type') or _get_field(rfq, 'type')
    timeline = _get_field(rfq, 'timeline_weeks') or _get_field(rfq, 'timeline')
    line_items = _get_field(rfq, 'line_items')
    vendor_requirements = _get_field(rfq, 'requirements') or _get_field(rfq, 'vendor_requirements')

    prompt = f"""
    RFQ:
    Subject: {subject}
    Scope: {scope}
    Sourcing Type: {sourcing}
    Timeline: {timeline}
    Line Items: {line_items}
    Vendor Requirements: {vendor_requirements}

    You are strictly forbidden from outputting anything except valid JSON.
    If you fail, you will be rejected. Generate structured vendor questions in JSON:
    {{
    "compliance": [],
    "experience": [],
    "timeline": [],
    "pricing": []
    }}
    """
    
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        result = response.json()
        response_text = result["response"]
        print(f"DEBUG - Ollama response: {response_text[:500]}")  # Print first 500 chars

        parsed = None
        # Try to parse the response as JSON
        try:
            cleaned = clean_json(response_text)
            parsed = json.loads(cleaned)
        except json.JSONDecodeError:
            print(f"WARNING - Response is not valid JSON. Extracting JSON from text...")
            # Try to find and extract JSON object
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                try:
                    json_str = response_text[start_idx:end_idx]
                    parsed = json.loads(json_str)
                except json.JSONDecodeError:
                    parsed = None

        # If still not parsed, build a fallback parsed structure
        if parsed is None:
            print(f"WARNING - Could not find JSON. Using fallback parsed structure...")
            parsed = {
                "compliance": [response_text[:200]],
                "experience": [],
                "timeline": [],
                "pricing": []
            }

        # Normalize parsed JSON into a list of question dicts
        questions = []
        if isinstance(parsed, dict):
            for category, items in parsed.items():
                if isinstance(items, list):
                    for it in items:
                        if isinstance(it, str):
                            questions.append({"question": it, "category": category, "required": True})
                        elif isinstance(it, dict) and "question" in it:
                            q = {"question": it.get("question"), "category": it.get("category", category), "required": it.get("required", True)}
                            questions.append(q)
                elif isinstance(items, str):
                    questions.append({"question": items, "category": category, "required": True})
        elif isinstance(parsed, list):
            for it in parsed:
                if isinstance(it, str):
                    questions.append({"question": it, "category": None, "required": True})
                elif isinstance(it, dict) and "question" in it:
                    questions.append({"question": it.get("question"), "category": it.get("category"), "required": it.get("required", True)})

        return {
            "questions": questions,
            "prompt": prompt,
            "raw_response": response_text
        }
    except requests.exceptions.RequestException as e:
        print(f"Error calling Ollama API: {e}")
        raise