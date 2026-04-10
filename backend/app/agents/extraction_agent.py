import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def extract_structured_data(raw_text):
    model = genai.GenerativeModel("gemini-2.5-pro")

    prompt = f"""
    Extract structured vendor data from text:

    {raw_text}

    Return JSON:
    {{
      "total_cost": "",
      "timeline": "",
      "scope_coverage": [],
      "terms": [],
      "currency": ""
    }}
    """

    response = model.generate_content(prompt)
    return response.text