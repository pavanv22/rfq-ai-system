import openai
import json
openai.api_base = "http://localhost:11434/v1"
openai.api_key = "not-needed"

# genai.configure(api_key=os.getenv("GEMINI_API_KEY")) # Added API key as env variable

# def extract_structured_data(raw_text):
#     model = genai.GenerativeModel("gemini-2.5-pro")

#     prompt = f"""
#     Extract structured vendor data from text.

#     Return STRICT JSON only.

#     Fields:
#     - vendor_name
#     - total_cost (number)
#     - currency
#     - timeline_weeks
#     - scope_coverage (list)
#     - key_terms (list)

#     Text:
#     {raw_text}
#     """

#     response = model.generate_content(prompt)

#     try:
#         return json.loads(response.text)
#     except:
#         return {"error": "Failed to parse", "raw": response.text}
def clean_json(text):
    return text.replace("```json", "").replace("```", "").strip()  

def extract_structured_data(raw_text):
    response = openai.ChatCompletion.create(
        model="llama-3-8b",
        messages=[
            {
                
            "role": "user", "content": 
            f"""
           Extract structured vendor data from text.

            You are strictly forbidden from outputting anything except valid JSON.
            If you fail, you will be rejected.

            Fields:
            - vendor_name
            - total_cost (number)
            - currency
            - timeline_weeks
            - scope_coverage (list)
            - key_terms (list)

            Text:
            {raw_text}
            """}
        ]
    )
    return json.loads(clean_json(response["choices"][0]["message"]["content"]))