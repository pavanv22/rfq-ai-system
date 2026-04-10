import streamlit as st
import requests

st.title("RFQ AI System")

tab1, tab2, tab3 = st.tabs(["RFQ", "Vendor", "Results"])

with tab1:
    st.header("Create RFQ")
    scope = st.text_area("Scope")
    timeline = st.text_input("Timeline")

    if st.button("Submit RFQ"):
        requests.post("http://localhost:8000/rfq/create", json={
            "title": "Test",
            "scope": scope,
            "timelines": timeline,
            "line_items": ["item1"]
        })

    if st.button("Generate Questions"):
        res = requests.get("http://localhost:8000/rfq/generate-questions")
        st.write(res.json())

with tab2:
    file = st.file_uploader("Upload Vendor File")
    if file:
        requests.post("http://localhost:8000/vendor/upload", files={"file": file})

with tab3:
    st.write("Results will appear here")