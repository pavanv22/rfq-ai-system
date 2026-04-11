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
                        st.session_state.rfq_id = resp["id"]
                    else:
                        st.error(f"❌ Error: {resp.get('error', 'Unknown error')}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    else:
        rfqs = api_call("GET", "/rfq/")
        if rfqs and not (isinstance(rfqs, dict) and rfqs.get("error")):
            rlist = rfqs if isinstance(rfqs, list) else [rfqs]
            if rlist:
                df_data = [{
                    "Project": r["project_name"][:30],
                    "Budget": fmt_curr(r.get("budget")),
                    "Timeline": f"{r.get('timeline_weeks')}w",
                    "Status": r.get("status", "pending"),
                    "ID": r["id"]
                } for r in rlist]
                
                df = pd.DataFrame(df_data)
                st.dataframe(df[["Project", "Budget", "Timeline", "Status"]], use_container_width=True, hide_index=True)
                
                if st.button("🔄 Refresh"):
                    st.rerun()

def tab_vendors():
    """Tab 2: Vendor Management"""
    st.markdown("### 🏢 Vendor Quotations")
    
    rfqs = api_call("GET", "/rfq/")
    if not rfqs or (isinstance(rfqs, dict) and rfqs.get("error")):
        st.warning("⚠️ No RFQs available. Create one in Tab 1 first.")
        return
    
    rlist = rfqs if isinstance(rfqs, list) else [rfqs]
    rfq_opts = {r["project_name"]: r["id"] for r in rlist}
    
    if not rfq_opts:
        st.warning("⚠️ No RFQs available")
        return
    
    sel_rfq_name = st.selectbox("📋 Select RFQ:", list(rfq_opts.keys()))
    sel_rfq_id = rfq_opts[sel_rfq_name]
    
    # File upload
    st.markdown("**Upload Vendor Response** (PDF, DOCX, PPTX, XLSX, PNG, JPG, TXT)")
    file = st.file_uploader("Choose file", type=["pdf", "docx", "pptx", "xlsx", "png", "jpg", "jpeg", "txt"])
    
    if file and st.button("📤 Upload & Process", use_container_width=True):
        with st.spinner("Processing vendor response..."):
            try:
                files_dict = {"file": file}
                resp = requests.post(f"{API_BASE_URL}/vendor/{sel_rfq_id}/upload", files=files_dict).json()
                
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
    rfq_opts = {r["project_name"]: r["id"] for r in rlist}
    
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
            st.warning(f"⚠️ Weights must sum to 1.0 (currently {total:.2f})")
        else:
            if st.button("▶️ Run Scoring", use_container_width=True):
                with st.spinner("Scoring vendors..."):
                    resp = api_call("POST", f"/analysis/{sel_rfq_id}/score", 
                                  params={"price_weight": p_weight, "delivery_weight": d_weight, 
                                         "compliance_weight": c_weight})
                    if resp.get("message"):
                        st.success("✅ Scoring completed!")
                    else:
                        st.error(f"❌ Error: {resp.get('detail', 'Unknown error')}")
    
    # Display results
    scores_resp = api_call("GET", f"/analysis/{sel_rfq_id}/scores")
    if scores_resp and not (isinstance(scores_resp, dict) and scores_resp.get("error")):
        scores_list = scores_resp if isinstance(scores_resp, list) else [scores_resp]
        
        if scores_list:
            st.markdown("#### 📊 Vendor Rankings")
            
            ranking_data = []
            for score in scores_list:
                ranking_data.append({
                    "Rank": score.get("rank", 0),
                    "Vendor": score.get("vendor_id", "N/A")[:20],
                    "Price": score.get("price_score", 0),
                    "Delivery": score.get("delivery_score", 0),
                    "Compliance": score.get("compliance_score", 0),
                    "Score": score.get("weighted_score", 0)
                })
            
            df_scores = pd.DataFrame(ranking_data)
            st.dataframe(df_scores, use_container_width=True, hide_index=True)
            
            # Show details for top vendor
            if scores_list and len(scores_list) > 0:
                best = scores_list[0]
                st.markdown("---")
                st.markdown(f"### 🏆 RECOMMENDED: **{best.get('vendor_id', 'N/A')}**")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Overall Score", f"{best.get('weighted_score', 0):.1f}/100")
                col2.metric("Price", f"{best.get('price_score', 0)}/10")
                col3.metric("Delivery", f"{best.get('delivery_score', 0)}/10")
                col4.metric("Compliance", f"{best.get('compliance_score', 0)}/10")
    else:
        st.info("Run scoring to see results")

# Main UI
st.title("📄 RFQ AI Vendor Evaluation System")

tab1, tab2, tab3 = st.tabs(["RFQ Submission", "Vendor Quotations", "Results & Scoring"])

with tab1:
    tab_rfq()

with tab2:
    tab_vendors()

with tab3:
    tab_results()

st.markdown("---")
st.caption("RFQ AI System v1.0 | FastAPI + Ollama + Streamlit")
