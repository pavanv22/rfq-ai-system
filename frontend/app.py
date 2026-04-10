"""RFQ AI System - Streamlit Frontend"""

import streamlit as st
import requests
import json
import pandas as pd

API_BASE_URL = "http://localhost:8001"
st.set_page_config(page_title="RFQ AI System", page_icon="📄", layout="wide")

def api_call(method: str, endpoint: str, data=None, files=None, params=None):
    """Make API call"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        if method == "POST":
            resp = requests.post(url, files=files, json=data if not files else None)
        elif method == "GET":
            resp = requests.get(url, params=params)
        elif method == "PUT":
            resp = requests.put(url, json=data)
        elif method == "DELETE":
            resp = requests.delete(url)
            return {"status": "deleted"}
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

def fmt_curr(val):
    return f"${val:,.2f}" if isinstance(val, (int, float)) else "N/A"

def tab_rfq():
    """Tab 1: RFQ Management"""
    st.markdown("### 📋 RFQ Submission")
    
    tab_mode = st.radio("Action", ["Create New RFQ", "View Existing RFQs"], horizontal=True, key="rfq_action")
    
    if tab_mode == "Create New RFQ":
        with st.form("create_rfq_form", clear_on_submit=False):
            col1, col2 = st.columns(2)
            with col1:
                project = st.text_input("Project Name*", key="rfq_proj")
                budget = st.number_input("Budget (USD)*", min_value=0, value=100000, step=1000, key="rfq_budget")
            with col2:
                timeline = st.number_input("Timeline (weeks)*", min_value=1, value=4, key="rfq_timeline")
                rtype = st.selectbox("Type", ["RFQ", "RFP", "RFI"], key="rfq_type")
            
            scope = st.text_area("Scope*", height=100, key="rfq_scope")
            
            if st.form_submit_button("✅ Create RFQ", use_container_width=True):
                try:
                    payload = {
                        "project_name": project,
                        "budget": float(budget),
                        "currency": "USD",
                        "timeline_weeks": int(timeline),
                        "sourcing_type": rtype,
                        "scope": scope,
                        "requirements": [],
                        "line_items": []
                    }
                    resp = api_call("POST", "/rfq/", data=payload)
                    if "id" in resp:
                        st.success(f"✅ RFQ Created! ID: {resp['id'][:8]}...")
                        st.balloons()
                    else:
                        st.error(f"❌ {resp.get('error', 'Unknown error')}")
                except Exception as e:
                    st.error(f"❌ {str(e)}")
    else:
        rfqs = api_call("GET", "/rfq/")
        if rfqs and not (isinstance(rfqs, dict) and rfqs.get("error")):
            rlist = rfqs if isinstance(rfqs, list) else [rfqs]
            if rlist:
                df_data = [{
                    "Project": r.get("project_name", "N/A")[:20],
                    "Budget": fmt_curr(r.get("budget", 0)),
                    "Timeline": f"{r.get('timeline_weeks', 0)}w",
                    "Status": r.get("status", "pending"),
                    "ID": r["id"]
                } for r in rlist]
                
                st.dataframe([{k: v for k, v in row.items() if k != "ID"} for row in df_data], use_container_width=True)
                
                sel_id = st.selectbox("Select RFQ to view:", [d["ID"] for d in df_data], 
                                     format_func=lambda x: next((d["Project"] for d in df_data if d["ID"] == x), ""),
                                     key="view_rfq_select")
                if sel_id:
                    rfq = next((r for r in rlist if r["id"] == sel_id), None)
                    if rfq:
                        col1, col2, col3 = st.columns(3)
                        col1.metric("💰 Budget", fmt_curr(rfq.get("budget", 0)))
                        col2.metric("⏱️ Timeline", f"{rfq.get('timeline_weeks', 0)} weeks")
                        col3.metric("📌 Status", rfq.get("status", "N/A").upper())
                        
                        if st.button("📝 Generate Questionnaire", key="gen_q_btn"):
                            with st.spinner("Generating..."):
                                qr = api_call("POST", f"/rfq/{sel_id}/generate-questions")
                                if "questions" in qr:
                                    st.success("✅ Done!")
                                    with st.expander("View Questions"):
                                        st.json(qr.get("questions", []))
                                else:
                                    st.error(f"❌ {qr.get('error', 'Failed')}")
            else:
                st.info("No RFQs found. Create one!")

def tab_vendors():
    """Tab 2: Vendor Management"""
    st.markdown("### 🏢 Vendor Quotations")
    
    rfqs = api_call("GET", "/rfq/")
    if not rfqs or (isinstance(rfqs, dict) and rfqs.get("error")):
        st.warning("No RFQs available. Create one first!")
        return
    
    rlist = rfqs if isinstance(rfqs, list) else [rfqs]
    if not rlist:
        st.warning("No RFQs found")
        return
    
    rfq_map = {r.get("project_name", "Unknown"): r["id"] for r in rlist}
    sel_rfq_name = st.selectbox("Select RFQ:", list(rfq_map.keys()), key="vendor_rfq_select")
    sel_rfq_id = rfq_map[sel_rfq_name]
    
    # Show RFQ info
    rfq_info = api_call("GET", f"/rfq/{sel_rfq_id}")
    if rfq_info:
        c1, c2, c3 = st.columns(3)
        c1.metric("💰 Budget", fmt_curr(rfq_info.get("budget", 0)))
        c2.metric("⏱️ Timeline", f"{rfq_info.get('timeline_weeks', 0)}w")
        c3.metric("📌 Status", rfq_info.get("status", "N/A").upper())
    
    # Upload section
    st.markdown("**Upload Vendor Response**")
    col_f, col_b = st.columns([4, 1])
    
    with col_f:
        file = st.file_uploader("Choose file (PDF, DOCX, PPTX, XLSX, TXT, PNG, JPG)", 
                               type=["pdf", "docx", "pptx", "xlsx", "txt", "png", "jpg", "jpeg"],
                               key="vendor_file_upload", label_visibility="collapsed")
    
    with col_b:
        if st.button("📤 Upload", key="vendor_upload_btn", use_container_width=True):
            if file:
                with st.spinner("Processing..."):
                    try:
                        url = f"{API_BASE_URL}/vendor/{sel_rfq_id}/upload"
                        resp = requests.post(url, files={"file": file}).json()
                        if "error" not in resp:
                            st.success(f"✅ {resp.get('vendor_name')} processed!")
                            st.info(f"Status: {resp.get('extraction_status')}")
                        else:
                            st.error(f"❌ {resp['error']}")
                    except Exception as e:
                        st.error(f"❌ {str(e)}")
    
    # List vendors
    st.markdown("**Uploaded Vendors**")
    vendors = api_call("GET", f"/vendor/rfq/{sel_rfq_id}")
    if vendors and not (isinstance(vendors, dict) and vendors.get("error")):
        vlist = vendors if isinstance(vendors, list) else [vendors]
        if vlist:
            df = pd.DataFrame([{
                "Name": v.get("vendor_name", "N/A"),
                "Cost (USD)": fmt_curr(v.get("total_cost_usd", 0)),
                "Timeline": f"{v.get('timeline_weeks', 'N/A')}w",
                "Status": v.get("extraction_status", "pending")
            } for v in vlist])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No vendors uploaded yet")

def tab_results():
    """Tab 3: Results & Scoring"""
    st.markdown("### 📊 Results & Recommendations")
    
    rfqs = api_call("GET", "/rfq/")
    if not rfqs or (isinstance(rfqs, dict) and rfqs.get("error")):
        st.warning("No RFQs available")
        return
    
    rlist = rfqs if isinstance(rfqs, list) else [rfqs]
    if not rlist:
        st.warning("No RFQs found")
        return
    
    rfq_map = {r.get("project_name", "Unknown"): r["id"] for r in rlist}
    sel_rfq_name = st.selectbox("Select RFQ:", list(rfq_map.keys()), key="results_rfq_select")
    sel_rfq_id = rfq_map[sel_rfq_name]
    
    # Scoring controls
    st.markdown("**⚙️ Scoring Configuration**")
    col1, col2, col3 = st.columns(3)
    with col1:
        price_w = st.slider("Price %", 0.0, 1.0, 0.4, 0.05, key="price_weight")
    with col2:
        delivery_w = st.slider("Delivery %", 0.0, 1.0, 0.3, 0.05, key="delivery_weight")
    with col3:
        compliance_w = st.slider("Compliance %", 0.0, 1.0, 0.3, 0.05, key="compliance_weight")
    
    total_w = price_w + delivery_w + compliance_w
    if abs(total_w - 1.0) > 0.01:
        st.warning(f"⚠️ Weights sum to {total_w:.2f}, should equal 1.0")
    
    if st.button("▶️ Run Scoring", use_container_width=True, key="run_scoring_btn"):
        with st.spinner("Scoring vendors..."):
            resp = api_call("POST", f"/analysis/{sel_rfq_id}/score",
                          params={"price_weight": price_w, "delivery_weight": delivery_w, 
                                 "compliance_weight": compliance_w})
            if "error" not in resp:
                st.success("✅ Scoring complete!")
            else:
                st.error(f"❌ {resp.get('error')}")
    
    # Results
    st.markdown("---")
    st.markdown("**📋 Vendor Rankings**")
    results = api_call("GET", f"/analysis/{sel_rfq_id}/results")
    
    if results and results.get("results"):
        df_results = pd.DataFrame([{
            "Rank": r.get("rank", "N/A"),
            "Vendor": r.get("vendor_name", "N/A"),
            "Cost (USD)": fmt_curr(r.get("total_cost_usd", 0)),
            "Timeline": f"{r.get('timeline_weeks', 'N/A')}w",
            "Score": f"{r.get('weighted_score', 0):.0f}/100"
        } for r in results.get("results", [])])
        st.dataframe(df_results, use_container_width=True, hide_index=True)
        
        # Details
        for r in results.get("results", []):
            score = r.get("weighted_score", 0)
            with st.expander(f"📊 {r.get('vendor_name')} (Score: {score:.0f}/100)", expanded=False):
                j = r.get("justifications", {})
                c1, c2, c3 = st.columns(3)
                c1.info(f"🏷️ Price\n{j.get('price', 'N/A')}")
                c2.info(f"📅 Delivery\n{j.get('delivery', 'N/A')}")
                c3.info(f"✅ Compliance\n{j.get('compliance', 'N/A')}")
        
        # Award
        if results.get("results"):
            best = results["results"][0]
            st.markdown("---")
            st.markdown(f"### 🏆 RECOMMENDED: **{best.get('vendor_name', 'N/A')}**")
            st.metric("Final Score", f"{best.get('weighted_score', 0):.1f}/100")
    else:
        st.info("Run scoring to see results")

# Main UI
st.title("📄 RFQ AI Vendor Evaluation System")

tab1, tab2, tab3 = st.tabs(["RFQ Submission", "Vendor Quotations", "Results"])

with tab1:
    tab_rfq()

with tab2:
    tab_vendors()

with tab3:
    tab_results()

st.markdown("---")
st.caption("RFQ AI System v1.0 | FastAPI + Ollama + Streamlit")
"""RFQ AI System - Streamlit Frontend"""

import streamlit as st
import requests
import json
import pandas as pd

# Configuration
API_BASE_URL = "http://localhost:8000"
st.set_page_config(page_title="RFQ AI System", page_icon="📄", layout="wide")

# ==================== Helper Functions ====================

def api_call(method: str, endpoint: str, data=None, files=None, params=None):
    """Make API call with error handling"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        if method == "POST":
            if files:
                resp = requests.post(url, files=files)
            else:
                resp = requests.post(url, json=data)
            return resp.json()
        elif method == "GET":
            resp = requests.get(url, params=params)
            return resp.json()
        elif method == "PUT":
            resp = requests.put(url, json=data)
            return resp.json()
        elif method == "DELETE":
            resp = requests.delete(url)
            return {"status": "deleted"}
    except Exception as e:
        return {"error": str(e)}

def fmt_curr(val):
    """Format value as USD currency"""
    return f"${val:,.2f}" if isinstance(val, (int, float)) else "N/A"

# ==================== Tab 1: RFQ Submission ====================

def tab1():
    st.markdown("### 📋 RFQ Submission")
    mode = st.radio("Mode", ["Create New RFQ", "View Existing"], horizontal=True)
    
    if mode == "Create New RFQ":
        with st.form("rfq_form"):
            col1, col2 = st.columns(2)
            with col1:
                project = st.text_input("Project Name*")
                budget = st.number_input("Budget (USD)*", min_value=0, value=100000, step=1000)
            with col2:
                timeline = st.number_input("Timeline (weeks)*", min_value=1, value=4)
                stype = st.selectbox("Type", ["RFQ", "RFP", "RFI"])
            
            scope = st.text_area("Scope*")
            reqs = st.text_area("Requirements (JSON)", '[\"requirement1\"]')
            items = st.text_area("Line Items (JSON)", '[{\"item\":\"item1\"}]')
            
            if st.form_submit_button("✅ Create RFQ"):
                try:
                    payload = {
                        "project_name": project,
                        "budget": float(budget),
                        "currency": "USD",
                        "timeline_weeks": int(timeline),
                        "sourcing_type": stype,
                        "scope": scope,
                        "requirements": json.loads(reqs) if reqs.strip() else [],
                        "line_items": json.loads(items) if items.strip() else []
                    }
                    resp = api_call("POST", "/rfq/", data=payload)
                    if "id" in resp:
                        st.success(f"✅ RFQ Created! ID: {resp['id'][:8]}...")
                        st.session_state.rfq_id = resp["id"]
                    else:
                        st.error(f"❌ Error: {resp.get('error', 'Unknown error')}")
                except json.JSONDecodeError:
                    st.error("❌ Invalid JSON format")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    else:
        rfqs = api_call("GET", "/rfq/")
        if rfqs and not rfqs.get("error"):
            rlist = rfqs if isinstance(rfqs, list) else [rfqs]
            if rlist:
                df_data = [{
                    "Project": r["project_name"][:25],
                    "Budget": fmt_curr(r.get("budget")),
                    "Timeline": f"{r.get('timeline_weeks')}w",
                    "Status": r.get("status", "pending"),
                    "ID": r["id"]
                } for r in rlist]
                
                df = pd.DataFrame(df_data)
                st.dataframe(df[["Project", "Budget", "Timeline", "Status"]], use_container_width=True)
                
                if df_data:
                    sel_id = st.selectbox("Select RFQ:", [d["ID"] for d in df_data], 
                                         format_func=lambda x: next((d["Project"] for d in df_data if d["ID"] == x), ""))
                    if sel_id:
                        rfq = next((r for r in rlist if r["id"] == sel_id), None)
                        if rfq:
                            col1, col2, col3 = st.columns(3)
                            col1.metric("Budget", fmt_curr(rfq.get("budget")))
                            col2.metric("Timeline", f"{rfq.get('timeline_weeks')} weeks")
                            col3.metric("Status", rfq.get("status", "N/A").title())
                            
                            if st.button("📝 Generate Questionnaire"):
                                with st.spinner("Generating questionnaire..."):
                                    qresp = api_call("POST", f"/rfq/{sel_id}/generate-questions")
                                    if "questions" in qresp:
                                        st.success("✅ Questionnaire generated!")
                                        st.json(qresp.get("questions", []))
                                    else:
                                        st.error(f"❌ {qresp.get('error', 'Failed')}")
            else:
                st.info("ℹ️ No RFQs found")
        else:
            st.error(f"❌ Failed to load RFQs: {rfqs.get('error', 'Unknown error')}")

# ==================== Tab 2: Vendor Quotations ====================

def tab2():
    st.markdown("### 🏢 Vendor Quotations")
    
    rfqs = api_call("GET", "/rfq/")
    if not rfqs or rfqs.get("error"):
        st.warning("⚠️ No RFQs available. Create one in Tab 1 first.")
        return
    
    rlist = rfqs if isinstance(rfqs, list) else [rfqs]
    rfq_opts = {r["project_name"]: r["id"] for r in rlist}
    
    if not rfq_opts:
        st.warning("⚠️ No RFQs available")
        return
    
    sel_rfq_name = st.selectbox("📋 Select RFQ:", list(rfq_opts.keys()))
    sel_rfq_id = rfq_opts[sel_rfq_name]
    
    # Show RFQ summary
    rfq = api_call("GET", f"/rfq/{sel_rfq_id}")
    if rfq:
        col1, col2, col3 = st.columns(3)
        col1.metric("Budget", fmt_curr(rfq.get("budget")))
        col2.metric("Timeline", f"{rfq.get('timeline_weeks')} weeks")
        col3.metric("Status", rfq.get("status", "N/A").title())
    
    # File upload
    st.markdown("**Upload Vendor Response** (PDF, DOCX, PPTX, XLSX, PNG, JPG, TXT)")
    col_file, col_btn = st.columns([3, 1])
    
    with col_file:
        file = st.file_uploader("Choose file", type=["pdf", "docx", "pptx", "xlsx", "png", "jpg", "jpeg", "txt"], 
                               label_visibility="collapsed")
    
    if file and col_btn.button("📤 Upload & Process"):
        with st.spinner("Processing file..."):
            try:
                url = f"{API_BASE_URL}/vendor/{sel_rfq_id}/upload"
                files_dict = {"file": file}
                resp = requests.post(url, files=files_dict).json()
                
                if "error" not in resp:
                    st.success("✅ Vendor response processed!")
                    st.info(f"**Vendor:** {resp.get('vendor_name')}")
                    st.info(f"**Status:** {resp.get('extraction_status')}")
                    if resp.get('missing_fields'):
                        st.warning(f"**Missing Fields:** {', '.join(resp.get('missing_fields', []))}")
                else:
                    st.error(f"❌ Error: {resp.get('error')}")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    # View uploaded vendors
    st.markdown("**Uploaded Vendors**")
    vendors = api_call("GET", f"/vendor/rfq/{sel_rfq_id}")
    if vendors and not vendors.get("error"):
        vlist = vendors if isinstance(vendors, list) else [vendors]
        if vlist:
            df = pd.DataFrame([{
                "Vendor": v["vendor_name"],
                "Cost (USD)": fmt_curr(v.get("total_cost_usd", 0)),
                "Timeline": f"{v.get('timeline_weeks', 'N/A')}w",
                "Status": v.get("extraction_status", "pending")
            } for v in vlist])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("ℹ️ No vendors uploaded yet")

# ==================== Tab 3: Results & Recommendations ====================

def tab3():
    st.markdown("### 📊 Results & Recommendations")
    
    rfqs = api_call("GET", "/rfq/")
    if not rfqs or rfqs.get("error"):
        st.warning("⚠️ No RFQs available")
        return
    
    rlist = rfqs if isinstance(rfqs, list) else [rfqs]
    rfq_opts = {r["project_name"]: r["id"] for r in rlist}
    
    if not rfq_opts:
        st.warning("⚠️ No RFQs available")
        return
    
    sel_rfq_name = st.selectbox("📋 Select RFQ:", list(rfq_opts.keys()), key="res_rfq")
    sel_rfq_id = rfq_opts[sel_rfq_name]
    
    # Scoring controls
    with st.expander("⚙️ Scoring Configuration", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            p_weight = st.slider("Price %", 0.0, 1.0, 0.4, 0.05)
        with col2:
            d_weight = st.slider("Delivery %", 0.0, 1.0, 0.3, 0.05)
        with col3:
            c_weight = st.slider("Compliance %", 0.0, 1.0, 0.3, 0.05)
        
        total = p_weight + d_weight + c_weight
        if abs(total - 1.0) > 0.01:
            st.warning(f"⚠️ Weights sum to {total:.2f}, should be 1.0")
        
        if st.button("▶️ Run Scoring", use_container_width=True):
            with st.spinner("Scoring vendors..."):
                resp = api_call("POST", f"/analysis/{sel_rfq_id}/score", 
                              params={"price_weight": p_weight, "delivery_weight": d_weight, 
                                     "compliance_weight": c_weight})
                if "error" not in resp:
                    st.success("✅ Scoring completed!")
                else:
                    st.error(f"❌ Error: {resp.get('error')}")
    
    # Display results
    results = api_call("GET", f"/analysis/{sel_rfq_id}/results")
    if results and results.get("results"):
        st.markdown("#### Vendor Rankings")
        df = pd.DataFrame([{
            "Rank": r.get("rank", "N/A"),
            "Vendor": r.get("vendor_name", "N/A"),
            "Cost (USD)": fmt_curr(r.get("total_cost_usd", 0)),
            "Timeline": f"{r.get('timeline_weeks', 'N/A')}w",
            "Score": f"{r.get('weighted_score', 0):.0f}/100"
        } for r in results.get("results", [])])
        st.dataframe(df, use_container_width=True)
        
        # Vendor details
        st.markdown("#### Score Breakdown")
        for r in results.get("results", []):
            score = r.get("weighted_score", 0)
            with st.expander(f"📋 {r.get('vendor_name')} (Score: {score:.0f}/100)"):
                j = r.get("justifications", {})
                col1, col2, col3 = st.columns(3)
                col1.info(f"**Price:** {j.get('price', 'N/A')}")
                col2.info(f"**Delivery:** {j.get('delivery', 'N/A')}")
                col3.info(f"**Compliance:** {j.get('compliance', 'N/A')}")
        
        # Award recommendation
        if results.get("results"):
            best = results["results"][0]
            st.markdown("---")
            st.success(f"🏆 **RECOMMENDED: {best.get('vendor_name', 'N/A')}**")
            st.metric("Final Score", f"{best.get('weighted_score', 0):.1f}/100")
    else:
        st.info("ℹ️ No scoring results yet. Upload vendors and run scoring.")

# ==================== Main App ====================

st.title("📄 RFQ AI Vendor Evaluation System")

tab1_col, tab2_col, tab3_col = st.tabs(["🗂️ RFQ Submission", "🏢 Vendor Quotations", "📊 Results"])

with tab1_col:
    tab1()

with tab2_col:
    tab2()

with tab3_col:
    tab3()

st.markdown("---")
st.caption("RFQ AI System v1.0 | Powered by FastAPI + Ollama + Streamlit")
"""RFQ AI System - Streamlit Frontend."""

import streamlit as st
import requests
import json
import pandas as pd
from typing import Dict

# Configuration
API_BASE_URL = "http://localhost:8000"
st.set_page_config(page_title="RFQ AI System", page_icon="📄", layout="wide")

# ==================== API Functions ====================

def api_call(method: str, endpoint: str, data=None, files=None, params=None):
    """Make API call."""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        if method == "POST":
            return requests.post(url, json=data).json() if not files else requests.post(url, files=files).json()
        elif method == "GET":
            return requests.get(url, params=params).json()
        elif method == "PUT":
            return requests.put(url, json=data).json()
        elif method == "DELETE":
            requests.delete(url)
            return {"status": "deleted"}
    except Exception as e:
        return {"error": str(e)}

def fmt_curr(val):
    """Format currency."""
    return f"${val:,.2f}" if val else "N/A"

# ==================== Tab 1: RFQ Submission ====================

def tab1():
    st.markdown("### 📋 RFQ Submission")
    mode = st.radio("Mode", ["Create New RFQ", "View Existing"], horizontal=True)
    
    if mode == "Create New RFQ":
        with st.form("rfq_form"):
            col1, col2 = st.columns(2)
            with col1:
                project = st.text_input("Project Name*")
                budget = st.number_input("Budget (USD)*", min_value=0, value=100000, step=1000)
            with col2:
                timeline = st.number_input("Timeline (weeks)*", min_value=1, value=4)
                stype = st.selectbox("Type", ["RFQ", "RFP", "RFI"])
            
            scope = st.text_area("Scope*")
            reqs = st.text_area("Requirements (JSON)", '[" requirement1"]')
            items = st.text_area("Line Items (JSON)", '[{"item":"item1"}]')
            
            if st.form_submit_button("Create RFQ"):
                try:
                    payload = {
                        "project_name": project,
                        "budget": budget,
                        "currency": "USD",
                        "timeline_weeks": timeline,
                        "sourcing_type": stype,
                        "scope": scope,
                        "requirements": json.loads(reqs) if reqs.strip() else [],
                        "line_items": json.loads(items) if items.strip() else []
                    }
                    resp = api_call("POST", "/rfq/", data=payload)
                    if "id" in resp:
                        st.success(f"✅ RFQ Created! ID: {resp['id'][:8]}...")
                        st.session_state.rfq_id = resp["id"]
                        if st.button("Generate Questionnaire"):
                            gen_resp = api_call("POST", f"/rfq/{resp['id']}/generate-questions")
                            st.json(gen_resp.get("questions", []))
                    else:
                        st.error(f"❌ Error: {resp.get('error')}")
                except json.JSONDecodeError:
                    st.error("Invalid JSON format")
    else:
        rfqs = api_call("GET", "/rfq/")
        if rfqs and not rfqs.get("error"):
            df_data = [{
                "Project": r["project_name"][:20],
                "Budget": fmt_curr(r["budget"]),
                "Timeline": f"{r['timeline_weeks']}w",
                "Status": r["status"],
                "ID": r["id"]
            } for r in (rfqs if isinstance(rfqs, list) else [rfqs])]
            
            if df_data:
                df = pd.DataFrame(df_data)
                st.dataframe(df[["Project", "Budget", "Timeline", "Status"]], use_container_width=True)
                
                sel_id = st.selectbox("Select RFQ:", [d["ID"] for d in df_data], format_func=lambda x: next(d["Project"] for d in df_data if d["ID"] == x))
                if sel_id:
                    rfq = next(r for r in (rfqs if isinstance(rfqs, list) else [rfqs]) if r["id"] == sel_id)
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Budget", fmt_curr(rfq["budget"]))
                    col2.metric("Timeline", f"{rfq['timeline_weeks']} weeks")
                    col3.metric("Status", rfq["status"].title())
            else:
                st.info("No RFQs found")
        else:
            st.error("Failed to load RFQs")

# ==================== Tab 2: Vendor Quotations ====================

def tab2():
    st.markdown("### 🏢 Vendor Quotations")
    
    rfqs = api_call("GET", "/rfq/")
    if not rfqs or rfqs.get("error"):
        st.warning("No RFQs available")
        return
    
    rlist = rfqs if isinstance(rfqs, list) else [rfqs]
    rfq_opts = {r["project_name"]: r["id"] for r in rlist}
    sel_rfq_name = st.selectbox("Select RFQ:", list(rfq_opts.keys()))
    sel_rfq_id = rfq_opts[sel_rfq_name]
    
    # Show RFQ summary
    rfq = api_call("GET", f"/rfq/{sel_rfq_id}")
    col1, col2, col3 = st.columns(3)
    col1.metric("Budget", fmt_curr(rfq.get("budget")))
    col2.metric("Timeline", f"{rfq.get('timeline_weeks')} weeks")
    col3.metric("Status", rfq.get("status", "N/A").title())
    
    # File upload
    st.markdown("**Upload Vendor Response** (PDF, DOCX, PPTX, XLSX, PNG, JPG)")
    col_file, col_name = st.columns([3, 1])
    with col_file:
        file = st.file_uploader("File", type=["pdf", "docx", "pptx", "xlsx", "png", "jpg", "jpeg"], label_visibility="collapsed")
    with col_name:
        vname = st.text_input("Vendor Name", "Optional", label_visibility="collapsed")
    
    if file and st.button("Upload & Process"):
        with st.spinner("Processing..."):
            try:
                url = f"{API_BASE_URL}/vendor/{sel_rfq_id}/upload"
                files_dict = {"file": file}
                resp = requests.post(url, files=files_dict).json()
                if "error" not in resp:
                    st.success("✅ Processed!")
                    st.json({"vendor": resp.get("vendor_name"), "status": resp.get("extraction_status"), "missing_fields": resp.get("missing_fields")})
                else:
                    st.error(f"❌ {resp['error']}")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    # View uploaded vendors
    st.markdown("**Uploaded Vendors**")
    vendors = api_call("GET", f"/vendor/rfq/{sel_rfq_id}")
    if vendors and not vendors.get("error"):
        vlist = vendors if isinstance(vendors, list) else [vendors] if vendors else []
        if vlist:
            df = pd.DataFrame([{
                "Vendor": v["vendor_name"],
                "Cost (USD)": fmt_curr(v.get("total_cost_usd")),
                "Timeline": f"{v.get('timeline_weeks', 'N/A')}w",
                "Status": v.get("extraction_status", "pending").title()
            } for v in vlist])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No vendors uploaded yet")

# ==================== Tab 3: Results Dashboard ====================

def tab3():
    st.markdown("### 📊 Results & Recommendations")
    
    rfqs = api_call("GET", "/rfq/")
    if not rfqs or rfqs.get("error"):
        st.warning("No RFQs available")
        return
    
    rlist = rfqs if isinstance(rfqs, list) else [rfqs]
    rfq_opts = {r["project_name"]: r["id"] for r in rlist}
    sel_rfq_name = st.selectbox("Select RFQ:", list(rfq_opts.keys()), key="res_rfq")
    sel_rfq_id = rfq_opts[sel_rfq_name]
    
    # Scoring controls
    with st.expander("⚙️ Scoring Weights", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            p_weight = st.slider("Price", 0.0, 1.0, 0.4, 0.05)
        with col2:
            d_weight = st.slider("Delivery", 0.0, 1.0, 0.3, 0.05)
        with col3:
            c_weight = st.slider("Compliance", 0.0, 1.0, 0.3, 0.05)
        
        total = p_weight + d_weight + c_weight
        if abs(total - 1.0) > 0.01:
            st.warning(f"Weights sum to {total:.2f}, should be 1.0")
        
        if st.button("Run Scoring"):
            with st.spinner("Scoring vendors..."):
                resp = api_call("POST", f"/analysis/{sel_rfq_id}/score", params={"price_weight": p_weight, "delivery_weight": d_weight, "compliance_weight": c_weight})
                if "error" not in resp:
                    st.success("✅ Scoring completed!")
                else:
                    st.error(f"❌ {resp['error']}")
    
    # Display results
    results = api_call("GET", f"/analysis/{sel_rfq_id}/results")
    if results and results.get("results"):
        st.markdown("**Vendor Rankings**")
        df = pd.DataFrame([{
            "Rank": r["rank"],
            "Vendor": r["vendor_name"],
            "Cost": fmt_curr(r.get("total_cost_usd")),
            "Timeline": f"{r.get('timeline_weeks')}w",
            "Score": f"{r.get('weighted_score', 0):.0f}/100"
        } for r in results["results"]])
        st.dataframe(df, use_container_width=True)
        
        # Details
        for r in results["results"]:
            with st.expander(f"📋 {r['vendor_name']} (Score: {r.get('weighted_score', 0):.0f})"):
                j = r.get("justifications", {})
                st.write(f"**Price:** {j.get('price', 'N/A')}")
                st.write(f"**Delivery:** {j.get('delivery', 'N/A')}")
                st.write(f"**Compliance:** {j.get('compliance', 'N/A')}")
        
        # Recommendation
        if results["results"]:
            best = results["results"][0]
            st.markdown("---")
            st.success(f"🏆 **Recommended: {best['vendor_name']}** (Score: {best.get('weighted_score', 0):.1f}/100)")
    else:
        st.info("Run scoring first to see results")

# ==================== Main App ====================

st.title("📄 RFQ AI Vendor Evaluation System")
tab1_col, tab2_col, tab3_col = st.tabs(["RFQ Submission", "Vendor Quotations", "Results"])

with tab1_col:
    tab1()
with tab2_col:
    tab2()
with tab3_col:
    tab3()

st.markdown("---")
st.caption("RFQ AI System v1.0 | FastAPI + Ollama + Streamlit")
import requests
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional

# ==================== Configuration ====================

API_BASE_URL = "http://localhost:8000"
PAGE_CONFIG = {
    "page_title": "RFQ AI System",
    "page_icon": "📄",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

st.set_page_config(**PAGE_CONFIG)

# Styling
st.markdown("""
    <style>
        .main-header {
            font-size: 2.5rem;
            color: #1f77b4;
            margin-bottom: 1rem;
        }
        .tab-header {
            font-size: 1.8rem;
            color: #1f77b4;
            border-bottom: 2px solid #1f77b4;
            padding-bottom: 0.5rem;
            margin-bottom: 1rem;
        }
        .status-badge {
            display: inline-block;
            padding: 0.5rem 1rem;
            border-radius: 0.3rem;
            font-size: 0.9rem;
            font-weight: bold;
        }
        .status-pending {
            background-color: #fdd835;
            color: #000;
        }
        .status-completed {
            background-color: #4caf50;
            color: #fff;
        }
        .status-incomplete {
            background-color: #f44336;
            color: #fff;
        }
    </style>
""", unsafe_allow_html=True)

# ==================== Helper Functions ====================

@st.cache_resource
def get_session_state():
    """Initialize session state."""
    if "current_rfq_id" not in st.session_state:
        st.session_state.current_rfq_id = None
    if "vendors_uploaded" not in st.session_state:
        st.session_state.vendors_uploaded = []
    return st.session_state


def make_api_call(
    method: str,
    endpoint: str,
    data: Dict = None,
    files: Dict = None,
    params: Dict = None
) -> tuple[bool, Dict]:
    """Make API call and return (success, response_data)."""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        headers = {} if method != "file" else None
        
        if method == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method == "GET":
            response = requests.get(url, params=params)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers)
        elif method == "DELETE":
            response = requests.delete(url)
        elif method == "file":
            response = requests.post(url, files=files)
        else:
            return False, {"error": f"Unknown method: {method}"}
        
        if response.status_code in [200, 201]:
            return True, response.json()
        else:
            return False, {"error": response.text, "status_code": response.status_code}
    except Exception as e:
        return False, {"error": str(e)}


def format_currency(value: float) -> str:
    """Format value as USD currency."""
    if value is None:
        return "N/A"
    return f"${value:,.2f}"


def display_rfq_summary(rfq: Dict):
    """Display RFQ information in a formatted way."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Project", rfq.get("project_name", "N/A")[:20])
    with col2:
        st.metric("Budget", format_currency(rfq.get("budget")))
    with col3:
        st.metric("Timeline", f"{rfq.get('timeline_weeks', 'N/A')} weeks")
    with col4:
        st.metric("Status", rfq.get("status", "unknown").title())


# ==================== TAB 1: RFQ Submission ====================

def tab_rfq_submission():
    """Tab 1: RFQ Submission - Customers submit RFQ details."""
    st.markdown('<div class="tab-header">📋 RFQ Submission</div>', unsafe_allow_html=True)
    
    # Mode selection
    col_mode1, col_mode2 = st.columns(2)
    with col_mode1:
        mode = st.radio("Choose action:", ["Create New RFQ", "View Existing RFQ"])
    
    # ---- Create New RFQ Mode ----
    if mode == "Create New RFQ":
        st.subheader("Create a New Request for Quotation")
        
        with st.form("create_rfq_form", clear_on_submit=True):
            # Basic Information
            col1, col2 = st.columns(2)
            with col1:
                project_name = st.text_input("Project Name*", placeholder="e.g., IT Infrastructure Upgrade")
                budget = st.number_input("Budget (USD)*", min_value=0.0, step=1000.0)
                currency = st.selectbox("Currency", ["USD", "EUR", "GBP", "INR"])
            
            with col2:
                timeline_weeks = st.number_input("Timeline (weeks)*", min_value=1, value=4)
                sourcing_type = st.selectbox("Sourcing Type", ["RFQ", "RFP", "RFI"])
                status = st.selectbox("Status", ["pending", "active", "closed"])
            
            # Scope and Details
            scope = st.text_area("Scope of Work*", placeholder="Describe what you need...")
            
            # Requirements (JSON)
            st.subheader("Vendor Requirements (JSON format)")
            requirements_json = st.text_area(
                "Requirements",
                value='["requirement1", "requirement2"]',
                height=100
            )
            
            # Line Items (JSON)
            st.subheader("Line Items (JSON format)")
            line_items_json = st.text_area(
                "Line Items",
                value='[{"item": "item1", "qty": 1, "unit": "unit"}]',
                height=100
            )
            
            submit_btn = st.form_submit_button("Create RFQ", use_container_width=True)
        
        if submit_btn:
            try:
                # Parse JSON fields
                requirements = json.loads(requirements_json) if requirements_json.strip() else []
                line_items = json.loads(line_items_json) if line_items_json.strip() else []
                
                rfq_data = {
                    "project_name": project_name,
                    "budget": budget,
                    "currency": currency,
                    "timeline_weeks": timeline_weeks,
                    "sourcing_type": sourcing_type,
                    "status": status,
                    "scope": scope,
                    "requirements": requirements,
                    "line_items": line_items
                }
                
                success, response = make_api_call("POST", "/rfq/", data=rfq_data)
                
                if success:
                    st.success(f"RFQ created successfully! ID: {response['id']}")
                    st.session_state.current_rfq_id = response['id']
                    
                    # Offer to generate questionnaire
                    st.info("Next step: Generate vendor questionnaire")
                    if st.button("Generate Questionnaire Now"):
                        st.session_state.go_to_gen_questions = True
                        st.rerun()
                else:
                    st.error(f"Failed to create RFQ: {response.get('error', 'Unknown error')}")
            except json.JSONDecodeError as e:
                st.error(f"Invalid JSON format: {e}")
    
    # ---- View Existing RFQ Mode ----
    else:
        st.subheader("View Existing RFQs")
        
        success, response = make_api_call("GET", "/rfq/")
        
        if success and response:
            rfqs = response if isinstance(response, list) else [response]
            
            if not rfqs:
                st.info("No RFQs found. Create one to get started!")
            else:
                # Create DataFrame for display
                rfq_data = []
                for rfq in rfqs:
                    rfq_data.append({
                        "ID": rfq["id"][:8] + "...",
                        "Project": rfq.get("project_name", "N/A"),
                        "Budget": format_currency(rfq.get("budget")),
                        "Timeline": f"{rfq.get('timeline_weeks')} weeks",
                        "Status": rfq.get("status", "unknown").title(),
                        "Created": rfq.get("created_at", "N/A")[:10],
                        "Full ID": rfq["id"]
                    })
                
                df = pd.DataFrame(rfq_data)
                
                # Display table
                st.markdown("### Existing RFQs")
                st.dataframe(df[["Project", "Budget", "Timeline", "Status", "Created"]], use_container_width=True)
                
                # Select RFQ
                selected_id = st.selectbox(
                    "Select an RFQ to view details:",
                    options=[r["Full ID"] for r in rfq_data],
                    format_func=lambda x: next(r["Project"] for r in rfq_data if r["Full ID"] == x)
                )
                
                if selected_id:
                    selected_rfq = next(r for r in rfqs if r["id"] == selected_id)
                    
                    st.markdown("### RFQ Details")
                    display_rfq_summary(selected_rfq)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Scope:**", selected_rfq.get("scope", "N/A"))
                    with col2:
                        st.write("**Sourcing Type:**", selected_rfq.get("sourcing_type", "N/A"))
                    
                    # Action buttons
                    col_btn1, col_btn2, col_btn3 = st.columns(3)
                    with col_btn1:
                        if st.button("View Questionnaire", use_container_width=True):
                            st.session_state.current_rfq_id = selected_id
                            st.switch_page("pages/questionnaire.py") if False else None  # Navigate
                    
                    with col_btn2:
                        if st.button("View Vendors", use_container_width=True):
                            st.session_state.current_rfq_id = selected_id
                    
                    with col_btn3:
                        if st.button("Generate Questionnaire", use_container_width=True):
                            # Generate questionnaire
                            with st.spinner("Generating questionnaire..."):
                                success, response = make_api_call(
                                    "POST",
                                    f"/rfq/{selected_id}/generate-questions"
                                )
                                
                                if success:
                                    st.success("Questionnaire generated successfully!")
                                    st.json(response.get("questions", []))
                                else:
                                    st.error(f"Failed to generate: {response.get('error')}")
        else:
            st.error(f"Failed to fetch RFQs: {response.get('error', 'Unknown error')}")


# ==================== TAB 2: Vendor Quotations ====================

def tab_vendor_quotations():
    """Tab 2: Vendor Quotations - Upload and manage vendor responses."""
    st.markdown('<div class="tab-header">🏢 Vendor Quotations</div>', unsafe_allow_html=True)
    
    # Step 1: Select RFQ
    st.subheader("Step 1: Select RFQ")
    success, rfqs_response = make_api_call("GET", "/rfq/")
    
    if not success or not rfqs_response:
        st.error("Failed to fetch RFQs")
        return
    
    rfqs = rfqs_response if isinstance(rfqs_response, list) else [rfqs_response]
    if not rfqs:
        st.warning("No RFQs available. Please create an RFQ first.")
        return
    
    rfq_options = {r["project_name"]: r["id"] for r in rfqs}
    selected_rfq_name = st.selectbox("Select RFQ:", options=list(rfq_options.keys()))
    selected_rfq_id = rfq_options[selected_rfq_name]
    
    # Get RFQ details
    success, rfq = make_api_call("GET", f"/rfq/{selected_rfq_id}")
    if success:
        display_rfq_summary(rfq)
        
        # Show questionnaire
        success, questionnaire = make_api_call("GET", f"/rfq/{selected_rfq_id}/questions")
        if success:
            with st.expander("📝 View Vendor Questionnaire"):
                if "questions" in questionnaire:
                    for i, q in enumerate(questionnaire["questions"], 1):
                        st.write(f"**Q{i}:** {q.get('question', 'N/A')}")
    
    # Step 2: Upload Vendor Files
    st.subheader("Step 2: Upload Vendor Responses")
    st.write("Supported formats: PDF, DOCX, PPTX, XLSX, PNG, JPG")
    
    col_upload1, col_upload2 = st.columns([2, 1])
    with col_upload1:
        uploaded_file = st.file_uploader(
            "Choose a vendor file",
            type=["pdf", "docx", "pptx", "xlsx", "png", "jpg", "jpeg"],
            label_visibility="collapsed"
        )
    
    with col_upload2:
        vendor_name = st.text_input("Vendor Name", placeholder="Optional", label_visibility="collapsed")
    
    if uploaded_file:
        col_submit1, col_submit2 = st.columns(2)
        with col_submit1:
            if st.button("Upload & Process", use_container_width=True):
                with st.spinner("Processing vendor file..."):
                    files = {"file": uploaded_file}
                    params = {"vendor_name": vendor_name} if vendor_name else {}
                    
                    success, response = make_api_call(
                        "file",
                        f"/vendor/{selected_rfq_id}/upload",
                        files=files
                    )
                    
                    if success:
                        st.success("File processed successfully!")
                        st.json({
                            "vendor_name": response.get("vendor_name"),
                            "extraction_status": response.get("extraction_status"),
                            "missing_fields": response.get("missing_fields"),
                        })
                    else:
                        st.error(f"Failed to process: {response.get('error')}")
    
    # Step 3: View Uploaded Vendors
    st.subheader("Step 3: Uploaded Vendors")
    success, vendors_response = make_api_call("GET", f"/vendor/rfq/{selected_rfq_id}")
    
    if success and vendors_response:
        vendors = vendors_response if isinstance(vendors_response, list) else [vendors_response]
        
        if vendors:
            vendors_df = pd.DataFrame([
                {
                    "Vendor": v.get("vendor_name", "Unknown"),
                    "Cost (USD)": format_currency(v.get("total_cost_usd")),
                    "Timeline": f"{v.get('timeline_weeks', 'N/A')} weeks",
                    "Status": v.get("extraction_status", "pending").title(),
                    "Missing Fields": len(v.get("missing_fields", []))
                }
                for v in vendors
            ])
            
            st.dataframe(vendors_df, use_container_width=True)
        else:
            st.info("No vendors uploaded yet for this RFQ.")
    elif not success:
        st.warning("No vendors uploaded yet for this RFQ.")


# ==================== TAB 3: Results Dashboard ====================

def tab_results_dashboard():
    """Tab 3: Results Dashboard - View scoring and recommendations."""
    st.markdown('<div class="tab-header">📊 Results & Recommendation</div>', unsafe_allow_html=True)
    
    # Step 1: Select RFQ
    st.subheader("Step 1: Select RFQ")
    success, rfqs_response = make_api_call("GET", "/rfq/")
    
    if not success or not rfqs_response:
        st.error("Failed to fetch RFQs")
        return
    
    rfqs = rfqs_response if isinstance(rfqs_response, list) else [rfqs_response]
    if not rfqs:
        st.warning("No RFQs available.")
        return
    
    rfq_options = {r["project_name"]: r["id"] for r in rfqs}
    selected_rfq_name = st.selectbox("Select RFQ:", options=list(rfq_options.keys()), key="results_rfq")
    selected_rfq_id = rfq_options[selected_rfq_name]
    
    # Step 2: Run Scoring (if not already done)
    st.subheader("Step 2: Run Vendor Scoring")
    
    col_score1, col_score2 = st.columns(2)
    
    with col_score1:
        with st.form("scoring_weights_form"):
            st.write("Scoring Weights:")
            price_weight = st.slider("Price Weight", 0.0, 1.0, 0.4, 0.1)
            delivery_weight = st.slider("Delivery Weight", 0.0, 1.0, 0.3, 0.1)
            compliance_weight = st.slider("Compliance Weight", 0.0, 1.0, 0.3, 0.1)
            
            if not (0.99 < price_weight + delivery_weight + compliance_weight < 1.01):
                st.warning(f"Weights sum to {price_weight + delivery_weight + compliance_weight}, should be 1.0")
            
            score_btn = st.form_submit_button("Run Scoring", use_container_width=True)
    
    if score_btn:
        with st.spinner("Scoring vendors..."):
            success, response = make_api_call(
                "POST",
                f"/analysis/{selected_rfq_id}/score",
                params={
                    "price_weight": price_weight,
                    "delivery_weight": delivery_weight,
                    "compliance_weight": compliance_weight
                }
            )
            
            if success:
                st.success("Scoring completed!")
            else:
                st.error(f"Scoring failed: {response.get('error')}")
    
    # Step 3: View Results
    st.subheader("Step 3: Vendor Ranking")
    
    success, results = make_api_call("GET", f"/analysis/{selected_rfq_id}/results")
    
    if not success:
        st.info("Please run scoring first.")
        return
    
    if success and results.get("results"):
        results_data = results["results"]
        
        # Create ranking table
        ranking_df = pd.DataFrame([
            {
                "Rank": r.get("rank"),
                "Vendor": r.get("vendor_name"),
                "Cost (USD)": format_currency(r.get("total_cost_usd")),
                "Timeline": f"{r.get('timeline_weeks')} weeks",
                "Price Score": f"{r.get('justifications', {}).get('price', 'N/A')[:20]}...",
                "Weighted Score": f"{r.get('weighted_score', 0):.1f}/100"
            }
            for r in results_data
        ])
        
        st.dataframe(ranking_df, use_container_width=True)
        
        # Detailed breakdown
        st.subheader("Detailed Score Breakdown")
        
        col_detail1, col_detail2 = st.columns(2)
        
        for idx, result in enumerate(results_data):
            if idx % 2 == 0:
                col = col_detail1
            else:
                col = col_detail2
            
            with col:
                with st.expander(f"📋 {result.get('vendor_name')}"):
                    st.write(f"**Rank:** {result.get('rank')}")
                    st.write(f"**Weighted Score:** {result.get('weighted_score'):.1f}/100")
                    
                    # Score breakdown
                    justifs = result.get("justifications", {})
                    st.write("**Score Justifications:**")
                    st.write(f"- Price: {justifs.get('price', 'N/A')}")
                    st.write(f"- Delivery: {justifs.get('delivery', 'N/A')}")
                    st.write(f"- Compliance: {justifs.get('compliance', 'N/A')}")
                    st.write(f"- Overall: {justifs.get('overall', 'N/A')}")
        
        # Recommendation
        st.subheader("🏆 Award Recommendation")
        if results_data:
            best = results_data[0]
            col_award1, col_award2 = st.columns([2, 1])
            
            with col_award1:
                st.success(f"**Recommended Vendor:** {best.get('vendor_name')}")
                st.write(f"**Score:** {best.get('weighted_score'):.1f}/100")
                st.write(f"**Cost:** {format_currency(best.get('total_cost_usd'))}")
            
            with col_award2:
                if len(results_data) > 1:
                    runner_up = results_data[1]
                    score_gap = best.get('weighted_score', 0) - runner_up.get('weighted_score', 0)
                    st.info(f"**Runner-up:** {runner_up.get('vendor_name')}\n**Gap:** {score_gap:.1f} points")
    else:
        st.info("No results available. Please ensure vendors are uploaded and scoring has been run.")


# ==================== Main App ====================

def main():
    """Main application entry point."""
    # Header
    st.markdown('<h1 class="main-header">📄 RFQ AI Vendor Evaluation System</h1>', unsafe_allow_html=True)
    
    # Initialize session
    get_session_state()
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["RFQ Submission", "Vendor Quotations", "Results Dashboard"])

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