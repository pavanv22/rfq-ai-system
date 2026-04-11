"""RFQ AI System - Streamlit Frontend with Explainability"""

import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime

API_BASE_URL = "http://localhost:8001"
st.set_page_config(page_title="RFQ AI System", page_icon="📄", layout="wide")

# Store extraction logs for traceability
if "extraction_logs" not in st.session_state:
    st.session_state.extraction_logs = []
if "scoring_logs" not in st.session_state:
    st.session_state.scoring_logs = []

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

def log_extraction_event(vendor_name, event_type, source, details):
    """Log extraction event for traceability"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "vendor_name": vendor_name,
        "event_type": event_type,
        "source": source,
        "details": details
    }
    st.session_state.extraction_logs.append(log_entry)
    return log_entry

def log_scoring_event(rfq_id, event_type, details):
    """Log scoring event for traceability"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "rfq_id": rfq_id,
        "event_type": event_type,
        "details": details
    }
    st.session_state.scoring_logs.append(log_entry)
    return log_entry

def show_extraction_explainability(vendor_data):
    """Display detailed extraction breakdown and traceability"""
    if not vendor_data:
        return
    
    with st.expander("📊 Extraction Details & Traceability", expanded=False):
        st.markdown("### Extracted Fields")
        
        # Show each extracted field with confidence and source
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Vendor Name",
                vendor_data.get("vendor_name", "N/A"),
                delta="High Confidence" if vendor_data.get("extraction_status") == "normalized" else "Needs Review"
            )
        
        with col2:
            st.metric(
                "Total Cost (USD)",
                fmt_curr(vendor_data.get("total_cost_usd", 0)),
                delta=vendor_data.get("currency", "Unknown")
            )
        
        with col3:
            st.metric(
                "Timeline",
                f"{vendor_data.get('timeline_weeks', 'N/A')} weeks",
                delta=f"Source: {vendor_data.get('file_type', 'unknown').upper()}"
            )
        
        # Data source and processing details
        st.markdown("### Processing Trace")
        trace_cols = st.columns(4)
        
        with trace_cols[0]:
            st.markdown("**Source Document**")
            st.caption(f"{vendor_data.get('file_type', 'unknown').upper()}")
        
        with trace_cols[1]:
            st.markdown("**Extraction Status**")
            st.caption(vendor_data.get("extraction_status", "pending").upper())
        
        with trace_cols[2]:
            st.markdown("**Scope Coverage**")
            scope = vendor_data.get("scope_coverage", [])
            st.caption(f"{len(scope)} items" if isinstance(scope, list) else "N/A")
        
        with trace_cols[3]:
            st.markdown("**Confidence**")
            confidence = "High" if vendor_data.get("extraction_status") == "normalized" else "Medium"
            st.caption(confidence)
        
        # Detailed field breakdown
        st.markdown("### Field Extraction Breakdown")
        field_details = pd.DataFrame([
            {"Field": "Vendor Name", "Value": vendor_data.get("vendor_name", "NOT EXTRACTED"), "Confidence": "High" if vendor_data.get("vendor_name") else "Low"},
            {"Field": "Total Cost", "Value": fmt_curr(vendor_data.get("total_cost_usd")), "Confidence": "High" if vendor_data.get("total_cost_usd") else "Low"},
            {"Field": "Currency", "Value": vendor_data.get("currency", "NOT EXTRACTED"), "Confidence": "High" if vendor_data.get("currency") else "Low"},
            {"Field": "Timeline (weeks)", "Value": str(vendor_data.get("timeline_weeks", "NOT EXTRACTED")), "Confidence": "High" if vendor_data.get("timeline_weeks") else "Low"},
            {"Field": "Scope Coverage", "Value": f"{len(vendor_data.get('scope_coverage', []))} items", "Confidence": "Medium"},
        ])
        st.dataframe(field_details, use_container_width=True, hide_index=True)
        
        # Scope details
        if vendor_data.get("scope_coverage"):
            st.markdown("### Scope Items Extracted")
            scope_items = vendor_data.get("scope_coverage", [])
            for idx, item in enumerate(scope_items, 1):
                st.caption(f"{idx}. {item}")
        
        # Key terms extracted
        if vendor_data.get("key_terms"):
            st.markdown("### Compliance Terms Detected")
            terms = vendor_data.get("key_terms", [])
            term_cols = st.columns(min(3, len(terms)))
            for idx, term in enumerate(terms):
                with term_cols[idx % len(term_cols)]:
                    st.info(f"✓ {term}")

def show_scoring_explainability(score_data, all_scores):
    """Display detailed scoring breakdown and methodology"""
    if not score_data:
        return
    
    with st.expander("🎯 Scoring Breakdown & Methodology", expanded=True):
        st.markdown("### Score Components")
        
        # Show individual component scores
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Price Score",
                f"{score_data.get('price_score', 0)}/10",
                delta="Lower is better"
            )
        
        with col2:
            st.metric(
                "Delivery Score",
                f"{score_data.get('delivery_score', 0)}/10",
                delta="Higher is better"
            )
        
        with col3:
            st.metric(
                "Compliance Score",
                f"{score_data.get('compliance_score', 0)}/10",
                delta="Higher is better"
            )
        
        with col4:
            st.metric(
                "Weighted Score",
                f"{score_data.get('weighted_score', 0):.1f}/100",
                delta=f"Rank #{score_data.get('rank', '?')}"
            )
        
        st.markdown("### Scoring Methodology")
        st.info("""
        **Weighted Score Calculation:**
        - 40% Price (lower cost = higher score)
        - 30% Delivery Timeline (faster = higher score)  
        - 30% Compliance (more requirements met = higher score)
        """)
        
        # Comparative analysis
        st.markdown("### Comparative Analysis")
        if all_scores and len(all_scores) > 1:
            comparison_data = []
            for score in all_scores:
                comparison_data.append({
                    "Vendor": score.get("vendor_name", "N/A")[:30],
                    "Price Score": score.get("price_score", 0),
                    "Delivery Score": score.get("delivery_score", 0),
                    "Compliance Score": score.get("compliance_score", 0),
                    "Overall": f"{score.get('weighted_score', 0):.1f}"
                })
            
            comp_df = pd.DataFrame(comparison_data)
            st.dataframe(comp_df, use_container_width=True, hide_index=True)
            
            # Normalized comparison chart
            st.markdown("#### Score Distribution")
            chart_data = pd.DataFrame({
                "Vendor": [s.get("vendor_name", "N/A")[:20] for s in all_scores],
                "Price": [s.get("price_score", 0) for s in all_scores],
                "Delivery": [s.get("delivery_score", 0) for s in all_scores],
                "Compliance": [s.get("compliance_score", 0) for s in all_scores]
            })
            st.bar_chart(chart_data.set_index("Vendor"))
        
        st.markdown("### Recommendation Justification")
        current_rank = score_data.get("rank", 0)
        if current_rank == 1:
            st.success("""
            ✅ **This vendor is recommended because:**
            - Highest overall weighted score
            - Balanced performance across all criteria
            - Meets compliance requirements
            """)
        else:
            st.warning(f"⚠️ Rank #{current_rank} - Not recommended. Review top-ranked vendors.")

def tab_rfq():
    """Tab 1: RFQ Management"""
    st.markdown("### RFQ Submission")
    
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
            
            if st.form_submit_button("Create RFQ", use_container_width=True):
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
                        rfq_id = resp["id"]
                        st.success(f"✅ RFQ Created! ID: {rfq_id[:8]}...")
                        st.session_state.rfq_id = rfq_id
                        log_scoring_event(rfq_id, "RFQ_CREATED", {"project": project, "budget": budget})
                    else:
                        st.error(f"❌ Error: {resp.get('error', 'Unknown error')}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        
        # Generate questions button outside the form
        if st.session_state.get("rfq_id"):
            st.markdown("---")
            if st.button("🤖 Generate AI Questions", use_container_width=True, key=f"gen_q_{st.session_state.rfq_id}"):
                with st.spinner("Generating questions..."):
                    q_resp = api_call("POST", f"/rfq/{st.session_state.rfq_id}/generate-questions")
                    if "id" in q_resp:
                        st.success("✅ Questions generated!")
                        st.json(q_resp.get("questions", []))
                    else:
                        st.error(f"❌ {q_resp.get('detail', 'Failed to generate questions')}")
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
    """Tab 2: Vendor Management with Extraction Transparency"""
    st.markdown("### Vendor Quotations & Extraction Traceability")
    
    rfqs = api_call("GET", "/rfq/")
    if not rfqs or (isinstance(rfqs, dict) and rfqs.get("error")):
        st.warning("⚠️ No RFQs available. Create one in Tab 1 first.")
        return
    
    rlist = rfqs if isinstance(rfqs, list) else [rfqs]
    rfq_opts = {r["project_name"]: r["id"] for r in rlist}
    
    if not rfq_opts:
        st.warning("No RFQs available")
        return
    
    sel_rfq_name = st.selectbox("Select RFQ:", list(rfq_opts.keys()))
    sel_rfq_id = rfq_opts[sel_rfq_name]
    
    # File upload with extraction explanation
    st.markdown("**Upload Vendor Response** (PDF, DOCX, PPTX, XLSX, PNG, JPG, TXT)")
    st.info("The system will automatically extract: Vendor Name, Total Cost, Timeline, & Scope Coverage")
    
    file = st.file_uploader("Choose file", type=["pdf", "docx", "pptx", "xlsx", "png", "jpg", "jpeg", "txt"])
    
    if file and st.button("📤 Upload & Process", use_container_width=True):
        with st.spinner("Processing vendor response..."):
            try:
                files_dict = {"file": file}
                resp = requests.post(f"{API_BASE_URL}/vendor/{sel_rfq_id}/upload", files=files_dict).json()
                
                if "error" not in resp:
                    vendor_name = resp.get('vendor_name', 'Unknown')
                    st.success(f"✅ {vendor_name} processed!")
                    st.info(f"📊 Status: {resp.get('extraction_status').upper()}")
                    
                    # Log extraction event
                    log_extraction_event(vendor_name, "VENDOR_UPLOADED", file.name, {
                        "file_size": file.size,
                        "extraction_status": resp.get('extraction_status')
                    })
                    
                    # Show extraction details
                    show_extraction_explainability(resp)
                else:
                    st.error(f"❌ {resp['error']}")
            except Exception as e:
                st.error(f"❌ {str(e)}")
    
    # List vendors with detailed traceability
    st.markdown("---")
    st.markdown("**Uploaded Vendors & Extraction Summary**")
    vendors = api_call("GET", f"/vendor/rfq/{sel_rfq_id}")
    if vendors and not (isinstance(vendors, dict) and vendors.get("error")):
        vlist = vendors if isinstance(vendors, list) else [vendors]
        if vlist:
            # Detailed vendor table
            vendor_details = []
            for v in vlist:
                vendor_details.append({
                    "Vendor": v.get("vendor_name", "N/A"),
                    "Cost (USD)": fmt_curr(v.get("total_cost_usd", 0)),
                    "Timeline": f"{v.get('timeline_weeks', 'N/A')}w",
                    "Status": v.get("extraction_status", "pending"),
                    "Source": v.get("file_type", "unknown").upper()
                })
            
            df_vendors = pd.DataFrame(vendor_details)
            st.dataframe(df_vendors, use_container_width=True, hide_index=True)
            
            # Expandable details for each vendor
            for v in vlist:
                with st.expander(f"📋 Details: {v.get('vendor_name', 'Unknown')}", expanded=False):
                    show_extraction_explainability(v)
        else:
            st.info("No vendors uploaded yet")

def tab_results():
    """Tab 3: Results & Scoring with Full Explainability"""
    st.markdown("### Results, Recommendations & Scoring Explainability")
    
    rfqs = api_call("GET", "/rfq/")
    if not rfqs or (isinstance(rfqs, dict) and rfqs.get("error")):
        st.warning("No RFQs available")
        return
    
    rlist = rfqs if isinstance(rfqs, list) else [rfqs]
    rfq_opts = {r["project_name"]: r["id"] for r in rlist}
    
    sel_rfq_name = st.selectbox("Select RFQ:", list(rfq_opts.keys()), key="res_rfq")
    sel_rfq_id = rfq_opts[sel_rfq_name]
    
    # Scoring controls with explanation
    with st.expander("⚙️ Scoring Configuration & Methodology", expanded=True):
        st.markdown("**Adjust Scoring Weights** (must total 100%)")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            p_weight = st.slider("💰 Price Weight", 0.0, 1.0, 0.4, 0.05)
        with col2:
            d_weight = st.slider("📅 Delivery Weight", 0.0, 1.0, 0.3, 0.05)
        with col3:
            c_weight = st.slider("✅ Compliance Weight", 0.0, 1.0, 0.3, 0.05)
        
        total = p_weight + d_weight + c_weight
        if abs(total - 1.0) > 0.01:
            st.warning(f"⚠️ Weights must sum to 1.0 (currently {total:.2f})")
        else:
            st.success(f"✅ Weights valid: {total:.2f}")
            
            if st.button("▶ Run Scoring Analysis", use_container_width=True):
                with st.spinner("Scoring vendors..."):
                    resp = api_call("POST", f"/analysis/{sel_rfq_id}/score", 
                                  params={"price_weight": p_weight, "delivery_weight": d_weight, 
                                         "compliance_weight": c_weight})
                    if resp.get("message"):
                        st.success("✅ Scoring completed!")
                        log_scoring_event(sel_rfq_id, "SCORING_COMPLETE", {
                            "price_weight": p_weight,
                            "delivery_weight": d_weight,
                            "compliance_weight": c_weight
                        })
                    else:
                        st.error(f"❌ Error: {resp.get('detail', 'Unknown error')}")
    
    # Display results with full explainability
    scores_resp = api_call("GET", f"/analysis/{sel_rfq_id}/scores")
    
    has_error = isinstance(scores_resp, dict) and (scores_resp.get("error") or scores_resp.get("detail"))
    
    if scores_resp and not has_error:
        scores_list = scores_resp if isinstance(scores_resp, list) else [scores_resp]
        
        if scores_list:
            st.markdown("---")
            st.markdown("### 📊 Vendor Rankings")
            
            # Ranking table with detailed metrics
            ranking_data = []
            for score in scores_list:
                ranking_data.append({
                    "Rank": score.get("rank", 0),
                    "Vendor": score.get("vendor_name", "N/A")[:40],
                    "Price 💰": score.get("price_score", 0),
                    "Delivery 📅": score.get("delivery_score", 0),
                    "Compliance ✅": score.get("compliance_score", 0),
                    "Score 🎯": f"{score.get('weighted_score', 0):.1f}"
                })
            
            df_scores = pd.DataFrame(ranking_data)
            st.dataframe(df_scores, use_container_width=True, hide_index=True)
            
            # Show details for top vendor with explainability
            if scores_list and len(scores_list) > 0:
                best = scores_list[0]
                st.markdown("---")
                st.markdown(f"### 🏆 RECOMMENDED: **{best.get('vendor_name', 'N/A')}**")
                
                # Key metrics
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Overall Score", f"{best.get('weighted_score', 0):.1f}/100")
                col2.metric("Price Score", f"{best.get('price_score', 0)}/10")
                col3.metric("Delivery Score", f"{best.get('delivery_score', 0)}/10")
                col4.metric("Compliance", f"{best.get('compliance_score', 0)}/10")
                
                # Show scoring breakdown
                show_scoring_explainability(best, scores_list)
    else:
        st.info("⏳ Run scoring analysis to see vendor rankings and detailed recommendations")

def tab_audit_trail():
    """Tab 4: Audit Trail & Traceability"""
    st.markdown("### 📋 Audit Trail & Complete Traceability")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Extraction Events")
        if st.session_state.extraction_logs:
            extraction_df = pd.DataFrame(st.session_state.extraction_logs)
            st.dataframe(extraction_df, use_container_width=True, hide_index=True)
        else:
            st.info("No extraction events yet")
    
    with col2:
        st.markdown("#### Scoring Events")
        if st.session_state.scoring_logs:
            scoring_df = pd.DataFrame(st.session_state.scoring_logs)
            st.dataframe(scoring_df, use_container_width=True, hide_index=True)
        else:
            st.info("No scoring events yet")
    
    st.markdown("---")
    st.markdown("#### All Events Timeline")
    all_events = []
    for log in st.session_state.extraction_logs:
        all_events.append({"Type": "EXTRACTION", **log})
    for log in st.session_state.scoring_logs:
        all_events.append({"Type": "SCORING", **log})
    
    if all_events:
        timeline_df = pd.DataFrame(all_events)
        timeline_df = timeline_df.sort_values("timestamp", ascending=False)
        st.dataframe(timeline_df, use_container_width=True, hide_index=True)
    else:
        st.info("No events logged yet")

# Main UI
st.title("🎯 RFQ AI Vendor Evaluation System")
st.markdown("*With Complete Explainability & Traceability*")

tab1, tab2, tab3, tab4 = st.tabs(["🗂️ RFQ Submission", "👥 Vendor Quotations", "🏆 Results & Scoring", "📋 Audit Trail"])

with tab1:
    tab_rfq()

with tab2:
    tab_vendors()

with tab3:
    tab_results()

with tab4:
    tab_audit_trail()

st.markdown("---")
st.caption("RFQ AI System v2.0 | FastAPI + Ollama + Streamlit | With Full Explainability & Audit Trails")
