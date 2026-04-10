import sys
from pathlib import Path

# Add parent directory to path so backend module can be imported
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import requests
import json
from backend.app.agents.questionnaire_agent import generate_questionnaire

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3-8b"

st.title("RFQ AI System")

tab1, tab2, tab3 = st.tabs(["RFQ", "Vendor", "Results"])

with tab1:
    st.header("Create RFQ")

    # if st.button("Submit RFQ"):
    #     requests.post("http://localhost:8000/rfq/create", json={
    #         "title": "Test",
    #         "scope": scope,
    #         "timelines": timeline,
    #         "line_items": ["item1"]
    #     })

    # if st.button("Generate Questions"):
    #     st.write("Calling backend...")
    #     res = requests.get("http://localhost:8000/rfq/generate-questions")
    #     if res.status_code == 200:
    #         try:
    #             st.json(res.json())
    #             st.write(res.json())
    #         except Exception:
    #             st.error("Invalid JSON response from backend")
    #             st.text(res.text)
    #     else:
    #         st.error(f"Request failed: {res.status_code}")
    #         st.text(res.text)

   
    # ---------------------------
    # CONFIG
    # ---------------------------


    # ---------------------------
    # PROMPT
    # ---------------------------
    def build_prompt(rfq):
        return f"""
                    You are a senior procurement analyst working in enterprise sourcing.

                    Return ONLY valid JSON. No markdown.

                    RFQ DETAILS:
                    Subject: {rfq['subject']}
                    Scope: {rfq['scope']}
                    Sourcing Type: {rfq['sourcing_type']}
                    Timeline: {rfq['timeline']}
                    Line Items: {rfq['line_items']}
                    Vendor Requirements: {rfq['vendor_requirements']}

                    OUTPUT:
                    {{
                    "compliance": [],
                    "experience": [],
                    "timeline": [],
                    "pricing": []
                    }}
                """


    # ---------------------------
    # LLM CALL
    # ---------------------------
    def generate_questions(prompt):
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False
            }
        )

        return response.json()["response"]


    # ---------------------------
    # STREAMLIT UI
    # ---------------------------
    st.set_page_config(page_title="RFQ AI System", layout="wide")

    st.title("📄 RFQ AI System")

    # ---- RFQ FORM ----
    with st.form("rfq_form"):
        col1, col2 = st.columns(2)

        with col1:
            subject = st.text_input("Subject")
            sourcing_type = st.selectbox("Sourcing Type", ["RFQ", "RFP", "RFI"])
            status = st.selectbox("Status", ["Draft", "Published"])

        with col2:
            rfp_code = st.text_input("RFP Code")
            round_no = st.selectbox("Round", ["Round 1", "Round 2"])

        scope = st.text_area("Scope")

        timeline = st.text_input("Timeline Summary")

        st.subheader("Line Items (JSON format)")
        line_items = st.text_area("Enter line items as JSON", value="[]")

        st.subheader("Vendor Requirements")
        vendor_requirements = st.text_area("Vendor requirements (JSON)", value="{}")

        submit = st.form_submit_button("Generate Questions")


    # ---- ACTION ----
    if submit:
        rfq = {
            "subject": subject,
            "scope": scope,
            "sourcing_type": sourcing_type,
            "timeline": timeline,
            "line_items": line_items,
            "vendor_requirements": vendor_requirements
        }

        prompt = build_prompt(rfq)

        st.subheader("🧠 Prompt Sent to LLM")
        st.code(prompt)

        with st.spinner("Generating questions..."):
            output = generate_questionnaire(rfq)

        st.subheader("📊 LLM Output")
        st.text(output)

        # Optional: try JSON parsing
        try:
            parsed = json.loads(output)
            st.json(parsed)
        except:
            st.warning("Model did not return valid JSON")
        







    
with tab2:
    file = st.file_uploader("Upload Vendor File")
    if file:
        requests.post("http://localhost:8000/vendor/upload", files={"file": file})


with tab3:
        st.header("Results & Recommendation")

        if st.button("Run Analysis"):
            res = requests.get("http://localhost:8000/analysis/run")
            data = res.json()

            st.subheader("Recommendation")
            st.write(data["recommendation"])

            st.subheader("Vendor Comparison")
            st.json(data["vendors"]) 
            #App reload