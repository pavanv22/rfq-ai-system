import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generate_questionnaire(rfq):
    model = genai.GenerativeModel("gemini-2.5-pro")

    prompt = f"""
    RFQ:
    Scope: {rfq.scope}
    Timelines: {rfq.timelines}
    Line Items: {rfq.line_items}

    Generate structured vendor questions in JSON:
    {{
      "compliance": [],
      "experience": [],
      "timeline": [],
      "pricing": []
    }}
    """

    response = model.generate_content(prompt)
    return response.text