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
MODEL = "llama3:8b"  # Updated model name

def clean_json(text):
    return text.replace("```json", "").replace("```", "").strip()  


def generate_questionnaire(rfq):
    print("DEBUG - Generating questionnaire with RFQ:", rfq)
    
    prompt = f"""
    RFQ:
    Subject: {rfq['subject']}
    Scope: {rfq['scope']}
    Sourcing Type: {rfq['sourcing_type']}
    Timeline: {rfq['timeline']}
    Line Items: {rfq['line_items']}
    Vendor Requirements: {rfq['vendor_requirements']}

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
        
        # Try to parse the response as JSON
        try:
            cleaned = clean_json(response_text)
            return json.loads(cleaned)
        except json.JSONDecodeError:
            print(f"WARNING - Response is not valid JSON. Extracting JSON from text...")
            # Try to find and extract JSON object
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                try:
                    json_str = response_text[start_idx:end_idx]
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    pass
            
            # If no valid JSON found, return the text as a fallback structure
            print(f"WARNING - Could not find JSON. Returning text as fallback...")
            return {
                "compliance": [response_text[:200]],
                "experience": [],
                "timeline": [],
                "pricing": []
            }
    except requests.exceptions.RequestException as e:
        print(f"Error calling Ollama API: {e}")
        raise