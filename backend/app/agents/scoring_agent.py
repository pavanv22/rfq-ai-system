import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-pro")

def score_vendor(vendor):
    prompt = f"""
    You are a procurement expert.

    Evaluate this vendor based on:
    - price competitiveness
    - delivery timeline
    - compliance
    - overall reliability

    Vendor Data:
    {json.dumps(vendor, indent=2)}

    Return JSON:
    {{
        "score": number (0-100),
        "justification": "short explanation"
    }}
    """

    response = model.generate_content(prompt)

    try:
        text = response.text.strip()
        return json.loads(text)
    except:
        return {
            "score": 50,
            "justification": "Fallback scoring"
        }