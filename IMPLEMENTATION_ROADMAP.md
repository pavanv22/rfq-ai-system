# Implementation Roadmap - Priority Fixes

## Overview
This document provides step-by-step implementation guidance to address the 3 critical gaps identified in the evaluation.

---

## 🔴 PRIORITY 1: Source Traceability (Critical for Trust & Explainability)

### Goal
Every extracted field must have a trail showing: *where it came from, how it was extracted, and confidence level*.

### Implementation Steps

#### Step 1.1: Extend Database Schema
Add a new `FieldSource` table to track origin of all extracted data:

```python
# Location: backend/app/models/database.py

from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime
from datetime import datetime

class FieldSourceModel(Base):
    """Tracks the origin, confidence, and extraction method of each vendor field."""
    __tablename__ = "field_sources"
    
    id = Column(Integer, primary_key=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    
    # What field? (total_cost, vendor_name, timeline_weeks, etc.)
    field_name = Column(String, nullable=False)
    field_value = Column(String, nullable=False)
    field_data_type = Column(String)  # "currency", "integer", "string", etc.
    
    # WHERE from document?
    source_type = Column(String)  # "explicit" | "inferred" | "imputed"
    document_section = Column(String)  # "pricing_table", "header", "footer", etc.
    page_number = Column(Integer, nullable=True)
    line_number = Column(Integer, nullable=True)
    
    # HOW was it extracted?
    extraction_method = Column(String)  # "llm" | "regex" | "native_parser" | "ocr"
    llm_model = Column(String)  # "ollama_llama3"
    extraction_confidence = Column(Float)  # 0.0 to 1.0
    
    # Audit trail
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String)  # "extraction_agent" | "normalizer_service" | "manual_entry"
    
    # Link back to original data
    raw_text_snippet = Column(String)  # First 500 chars of source text
    
    __table_args__ = (
        Index('idx_vendor_field', 'vendor_id', 'field_name'),
    )

# Add relationship to VendorModel:
class VendorModel(Base):
    # ... existing fields ...
    field_sources = relationship("FieldSourceModel", back_populates="vendor")

class FieldSourceModel(Base):
    # ... existing fields ...
    vendor = relationship("VendorModel", back_populates="field_sources")
```

#### Step 1.2: Modify Extractor to Record Sources
Update extractor to track where data came from:

```python
# Location: backend/app/services/extractor.py

class ExtractedField:
    """Represents an extracted field with provenance."""
    def __init__(self, name, value, source_type, extraction_method, 
                 confidence=1.0, document_section=None, page=None):
        self.name = name
        self.value = value
        self.source_type = source_type  # "explicit" or "inferred"
        self.extraction_method = extraction_method  # "llm", "regex", "parser"
        self.confidence = confidence  # 0.0-1.0
        self.document_section = document_section
        self.page_number = page
        self.raw_text_snippet = ""

class VendorExtractor:
    def extract_with_sources(self, raw_text, file_type="txt"):
        """Extract vendor data and track source of each field."""
        
        # Call LLM extraction
        llm_result = self._extract_with_llm(raw_text)
        
        extracted_fields = []
        
        if llm_result and not llm_result.error:
            for field_name, value in llm_result.data.items():
                field = ExtractedField(
                    name=field_name,
                    value=value,
                    source_type="explicit",  # Came from LLM parsing
                    extraction_method="llm",
                    confidence=0.85,  # Slightly lower than hardcoded confidence
                    document_section=self._identify_section(raw_text, value)[0],
                    page=1  # TODO: Track actual page if from PDF
                )
                extracted_fields.append(field)
        else:
            # Fallback to regex
            regex_results = self._extract_with_regex(raw_text)
            for field_name, value in regex_results.items():
                field = ExtractedField(
                    name=field_name,
                    value=value,
                    source_type="explicit",
                    extraction_method="regex",
                    confidence=0.6,  # Lower confidence for regex
                    document_section=self._identify_section(raw_text, value)[0]
                )
                extracted_fields.append(field)
        
        return extracted_fields  # Now returns objects, not dict

    def _identify_section(self, text, value):
        """Identify which section of document the value came from."""
        sections = {
            "header": text[:text.find("\n\n")] if "\n\n" in text else text[:500],
            "body": text[text.find("\n\n"):] if "\n\n" in text else "",
            "table": "table" if "table" in text.lower() or "|" in text else None,
        }
        # Simple heuristic: where does value appear first?
        for section_name, section_text in sections.items():
            if section_text and str(value) in section_text:
                return section_name, text.find(str(value))
        return "body", 0
```

#### Step 1.3: Store Source Information in DB
When saving vendor data, also save field sources:

```python
# Location: backend/app/routes/vendor.py

@router.post("/{rfq_id}/upload")
async def upload_vendor(
    rfq_id: int, 
    file: UploadFile = File(...)
):
    # ... existing code to extract file text ...
    
    # NEW: Use extractor that returns sources
    extracted_fields = extractor.extract_with_sources(raw_text)
    
    # Store vendor data
    vendor_data = {field.name: field.value for field in extracted_fields}
    vendor = VendorModel(rfq_id=rfq_id, raw_extracted_data=vendor_data)
    db.add(vendor)
    db.commit()
    
    # NEW: Store field sources
    from models.database import FieldSourceModel
    for field in extracted_fields:
        source = FieldSourceModel(
            vendor_id=vendor.id,
            field_name=field.name,
            field_value=str(field.value),
            source_type=field.source_type,
            extraction_method=field.extraction_method,
            extraction_confidence=field.confidence,
            document_section=field.document_section,
            page_number=field.page_number,
            created_by="extraction_agent"
        )
        db.add(source)
    db.commit()
    
    return {...}
```

#### Step 1.4: API Endpoint to Retrieve Field Sources
Add endpoint to fetch field provenance for UI display:

```python
# Location: backend/app/routes/vendor.py

@router.get("/{vendor_id}/field-sources")
async def get_field_sources(vendor_id: int, db: Session = Depends(get_db)):
    """Get the source/provenance of all fields for a vendor."""
    sources = db.query(FieldSourceModel)\
        .filter(FieldSourceModel.vendor_id == vendor_id)\
        .all()
    
    return {
        field.field_name: {
            "value": field.field_value,
            "source_type": field.source_type,
            "extraction_method": field.extraction_method,
            "confidence": field.extraction_confidence,
            "section": field.document_section,
            "page": field.page_number,
            "raw_snippet": field.raw_text_snippet
        }
        for field in sources
    }
```

#### Step 1.5: Update Frontend to Show Sources
Display source information when showing vendor data:

```python
# Location: frontend/app.py (add to Vendor tab)

import streamlit as st
import requests

# ... existing vendor selection code ...

if selected_vendor:
    # Get vendors details AND sources
    vendor_resp = requests.get(f"http://localhost:8000/vendor/{selected_vendor['id']}")
    vendor_data = vendor_resp.json()
    
    # NEW: Get field sources
    sources_resp = requests.get(f"http://localhost:8000/vendor/{selected_vendor['id']}/field-sources")
    field_sources = sources_resp.json()
    
    # Display with source information
    st.write("### Extracted Vendor Data (with Source Tracking)")
    
    for field_name, value in vendor_data.items():
        source_info = field_sources.get(field_name, {})
        
        # Create display with confidence indicator
        confidence = source_info.get("confidence", 1.0)
        source_type = source_info.get("source_type", "unknown")
        extraction_method = source_info.get("extraction_method", "unknown")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            st.write(f"**{field_name}**")
        with col2:
            st.write(f"{value}")
        with col3:
            # Show confidence indicator
            if source_type == "inferred":
                st.warning(f"⚠️ Inferred (confidence: {confidence:.0%})")
            elif source_type == "explicit":
                if confidence >= 0.9:
                    st.success(f"✓ Explicit ({extraction_method})")
                else:
                    st.info(f"ℹ️ Explicit but uncertain (confidence: {confidence:.0%})")
            else:
                st.write(f"? {source_type} ({extraction_method})")
        
        # Show expandable details
        with st.expander(f"📍 Source details for {field_name}"):
            st.write(f"**Extraction Method**: {extraction_method}")
            st.write(f"**Confidence**: {confidence:.0%}")
            st.write(f"**Source Type**: {source_type}")
            st.write(f"**Document Section**: {source_info.get('section')}")
            if source_info.get('page'):
                st.write(f"**Page**: {source_info.get('page')}")
            if source_info.get('raw_snippet'):
                st.write(f"**Raw Text**: {source_info.get('raw_snippet')}")
```

---

## 🔴 PRIORITY 2: Scoring Grounding & Validation

### Goal
Every score must show *why* it was given and *what data* drove the decision.

### Implementation Steps

#### Step 2.1: Extend ScoreModel with Justification
```python
# Location: backend/app/models/database.py

class ScoreModel(Base):
    """Vendor scores with reasoning and source data."""
    __tablename__ = "scores"
    
    # ... existing fields ...
    
    price_score = Column(Integer)
    price_score_justification = Column(String)  # NEW: Why this score?
    price_score_source_data = Column(JSON)  # NEW: What data was used?
    # Example: {"vendor_cost": 47000, "rfq_budget": 72000, "ratio": 0.65}
    
    delivery_score = Column(Integer)
    delivery_score_justification = Column(String)
    delivery_score_source_data = Column(JSON)
    
    compliance_score = Column(Integer)
    compliance_score_justification = Column(String)
    compliance_score_source_data = Column(JSON)
    
    weighted_score = Column(Float)
    overall_justification = Column(String)  # NEW: Why is this the best/worst?
```

#### Step 2.2: Add Validation Layer
```python
# Location: backend/app/services/scoring.py (NEW FILE)

class ScoreValidator:
    """Validates that scores make sense based on the data."""
    
    def validate_price_score(self, score, vendor_cost, rfq_budget):
        """
        Sanity check: Price score should reflect cost vs budget.
        - If cost >> budget, score should be low (3-5)
        - If cost << budget, score should be high (7-9)
        """
        if vendor_cost is None or rfq_budget is None:
            return score, 0.5, "Missing data for validation"
        
        ratio = vendor_cost / rfq_budget if rfq_budget > 0 else 1.0
        
        if score < 3 and ratio < 0.5:
            return score, 0.3, f"⚠️ RISKY: Low score ({score}) but cost is {ratio:.0%} of budget"
        if score > 8 and ratio > 1.5:
            return score, 0.2, f"⚠️ RISKY: High score ({score}) but cost is {ratio:.0%} over budget"
        
        return score, 1.0, "✓ Valid"
    
    def validate_delivery_score(self, score, vendor_timeline, rfq_timeline):
        """Delivery score should reflect schedule alignment."""
        if vendor_timeline is None or rfq_timeline is None:
            return score, 0.5, "Missing timeline data"
        
        if score > 8 and vendor_timeline > rfq_timeline * 1.5:
            return score, 0.3, f"⚠️ Vendor timeline ({vendor_timeline}w) exceeds RFQ need ({rfq_timeline}w)"
        
        return score, 1.0, "✓ Valid"

    def validate_all_scores(self, scores_dict, vendor_data, rfq_data):
        """Run all validations and collect confidence levels."""
        results = {}
        
        price_score, price_conf, price_msg = self.validate_price_score(
            scores_dict['price_score'],
            vendor_data.get('total_cost_usd'),
            rfq_data.get('budget')
        )
        results['price'] = {
            'score': price_score,
            'confidence': price_conf,
            'message': price_msg
        }
        
        # ... similar for other scores ...
        
        return results
```

#### Step 2.3: Modify Scoring Agent to Return Justification
```python
# Location: backend/app/agents/scoring_agent.py

def score_vendor(vendor_data: dict, rfq_data: dict) -> dict:
    """Score a vendor on price, delivery, compliance with justifications."""
    
    # Enhanced prompt to get reasoning
    prompt = f"""
VENDOR DATA:
- Name: {vendor_data['vendor_name']}
- Cost: ${vendor_data['total_cost_usd']}
- Timeline: {vendor_data['timeline_weeks']} weeks
- Scope Coverage: {vendor_data['scope_coverage']}

RFQ REQUIREMENTS:
- Budget: ${rfq_data['budget']}
- Timeline: {rfq_data['timeline_weeks']} weeks
- Scope: {rfq_data['scope']}
- Type: {rfq_data['sourcing_type']}

Please score this vendor on the following scale (1-10):
1. PRICE (1=Very expensive, 10=Best value): 
   - Give a score from 1-10
   - Explain your reasoning (e.g., "Cost is $X vs budget $Y, which is Z% difference")
   
2. DELIVERY (1=Too slow, 10=Fastest):
   - Score: 1-10
   - Reasoning: (compare timeline days)

3. COMPLIANCE (1=Misses requirements, 10=Perfect fit):
   - Score: 1-10
   - Reasoning: (which requirements met/missed)

Output as JSON:
{{
    "price_score": <int 1-10>,
    "price_justification": "<explanation>",
    "price_source_data": {{"cost": <int>, "budget": <int>, "difference_percent": <float>}},
    
    "delivery_score": <int 1-10>,
    "delivery_justification": "<explanation>",
    "delivery_source_data": {{"vendor_timeline": <int>, "rfq_timeline": <int>}},
    
    "compliance_score": <int 1-10>,
    "compliance_justification": "<explanation>"
}}
"""
    
    response = call_ollama(prompt)
    scores = parse_json_response(response)
    
    # NEW: Validate scores make sense
    from services.scoring_validator import ScoreValidator
    validator = ScoreValidator()
    validation_results = validator.validate_all_scores(
        {
            'price_score': scores['price_score'],
            'delivery_score': scores['delivery_score'],
            'compliance_score': scores['compliance_score']
        },
        vendor_data,
        rfq_data
    )
    
    # Add validation warnings to response
    scores['validation'] = validation_results
    
    return scores
```

#### Step 2.4: Store Scores with Justification
```python
# Location: backend/app/routes/analysis.py

@router.post("/{rfq_id}/score")
async def score_vendors(rfq_id: int, weights: dict, db: Session = Depends(get_db)):
    """Score all vendors with grounding."""
    
    rfq = db.query(RFQModel).filter(RFQModel.id == rfq_id).first()
    vendors = db.query(VendorModel).filter(VendorModel.rfq_id == rfq_id).all()
    
    for vendor in vendors:
        # Score with agent
        scores = score_vendor(vendor.normalized_data, rfq_to_dict(rfq))
        
        # NEW: Calculate weighted score
        weighted = (
            scores['price_score'] * weights.get('price', 0.4) +
            scores['delivery_score'] * weights.get('delivery', 0.3) +
            scores['compliance_score'] * weights.get('compliance', 0.3)
        )
        
        # NEW: Store with justification
        score_record = ScoreModel(
            vendor_id=vendor.id,
            rfq_id=rfq_id,
            price_score=scores['price_score'],
            price_score_justification=scores['price_justification'],
            price_score_source_data=scores['price_source_data'],
            delivery_score=scores['delivery_score'],
            delivery_score_justification=scores['delivery_justification'],
            delivery_score_source_data=scores['delivery_source_data'],
            compliance_score=scores['compliance_score'],
            compliance_score_justification=scores['compliance_justification'],
            weighted_score=weighted,
            overall_justification=f"Price: {scores['price_justification']} | Delivery: {scores['delivery_justification']}"
        )
        db.add(score_record)
    
    db.commit()
    return {"status": "success", "scores_created": len(vendors)}
```

#### Step 2.5: Update Frontend to Show Scoring Reasoning
```python
# Location: frontend/app.py (Results tab)

import requests
import pandas as pd

# NEW: Results Tab
with st.tabs(["RFQs", "Vendors", "Results"]):
    # ... existing tabs ...
    
    with st.tab("Results"):
        rfq_id = st.selectbox("Select RFQ", [r.id for r in rfqs])
        
        # Fetch scores
        resp = requests.get(f"http://localhost:8000/analysis/{rfq_id}/scores")
        scores = resp.json()
        
        # Display ranking
        st.write("### Vendor Ranking")
        
        ranked = sorted(scores, key=lambda x: x['weighted_score'], reverse=True)
        
        for rank, vendor_score in enumerate(ranked, 1):
            with st.expander(f"#{rank} - {vendor_score['vendor_name']} (Score: {vendor_score['weighted_score']:.0f}/100)"):
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Price Score", vendor_score['price_score'], "/10")
                    st.write(f"**Why**: {vendor_score['price_score_justification']}")
                    source = vendor_score['price_score_source_data']
                    st.write(f"Cost: ${source['cost']:,} vs Budget: ${source['budget']:,}")
                
                with col2:
                    st.metric("Delivery Score", vendor_score['delivery_score'], "/10")
                    st.write(f"**Why**: {vendor_score['delivery_score_justification']}")
                
                with col3:
                    st.metric("Compliance Score", vendor_score['compliance_score'], "/10")
                    st.write(f"**Why**: {vendor_score['compliance_score_justification']}")
                
                st.divider()
                st.write(f"**Overall**: {vendor_score['overall_justification']}")
```

---

## 🟠 PRIORITY 3: UX Polish & Visual Comparisons

### Goal
Make results visually clear, comparable, and trustworthy for business users.

### Implementation Steps

#### Step 3.1: Add Vendor Review Tab
Before scoring, let users review extracted data:

```python
# Location: frontend/app.py

with st.tab("Vendors"):
    # ... existing upload code ...
    
    # NEW: Review Section
    st.write("### Review Extracted Vendor Data")
    
    reviewed_vendors = []
    for vendor in vendors:
        with st.expander(f"✎ Review: {vendor['vendor_name']}", expanded=False):
            
            # Show each field with source
            for field_name, field_data in vendor['fields_with_sources'].items():
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                
                with col1:
                    reviewed_value = st.text_input(
                        field_name,
                        value=str(field_data['value']),
                        key=f"{vendor['id']}_{field_name}"
                    )
                
                with col2:
                    st.write(f"**From**: {field_data['source_type']}")
                
                with col3:
                    confidence = field_data['confidence']
                    color = "green" if confidence >= 0.9 else "orange" if confidence >= 0.7 else "red"
                    st.metric("Confidence", f"{confidence:.0%}")
                
                with col4:
                    if st.button("ⓘ Details", key=f"details_{vendor['id']}_{field_name}"):
                        st.write(f"Document section: {field_data.get('section')}")
                        st.write(f"Extraction method: {field_data.get('method')}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✓ Approve", key=f"approve_{vendor['id']}"):
                    st.success("Vendor approved for scoring!")
            with col2:
                if st.button("✕ Reject", key=f"reject_{vendor['id']}"):
                    st.error("Vendor removed")
```

#### Step 3.2: Add Comparison Charts
```python
# Location: frontend/app.py (Results tab)

import plotly.graph_objects as go
import plotly.express as px

# Comparison Chart
vendors_comparison = pd.DataFrame(scores)

# Radar chart for multi-criteria comparison
fig = go.Figure()

for _, vendor in vendors_comparison.iterrows():
    fig.add_trace(go.Scatterpolar(
        r=[vendor['price_score'], vendor['delivery_score'], vendor['compliance_score']],
        theta=['Price', 'Delivery', 'Compliance'],
        fill='toself',
        name=vendor['vendor_name']
    ))

fig.update_layout(
    polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
    showlegend=True,
    title="Vendor Score Comparison (Radar Chart)"
)
st.plotly_chart(fig, use_container_width=True)

# Bar chart for weighted scores
fig_bar = px.bar(
    vendors_comparison.sort_values('weighted_score', ascending=False),
    x='vendor_name',
    y='weighted_score',
    color='weighted_score',
    title='Vendor Weighted Scores',
    range_y=[0, 100],
    text='weighted_score'
)
st.plotly_chart(fig_bar, use_container_width=True)
```

#### Step 3.3: Add Cost Comparison Table
```python
# Location: frontend/app.py

# Cost breakdown
st.write("### Cost Analysis")

cost_comparison = pd.DataFrame([
    {
        'Vendor': v['vendor_name'],
        'Quoted Cost': f"${v['total_cost_usd']:,.0f}",
        'vs Budget': f"{(v['total_cost_usd']/rfq['budget']*100):.0f}%",
        'Difference': f"${v['total_cost_usd'] - rfq['budget']:+,.0f}",
        'Monthly Cost': f"${v['total_cost_usd']/v['timeline_weeks']/4:,.0f}"
    }
    for v in vendors
])

# Color-code the "vs Budget" column
def highlight_budget(val):
    if '%' in val:
        pct = int(val.replace('%', ''))
        if pct > 120:
            return 'background-color: #ff4444'  # Red: over budget
        elif pct < 100:
            return 'background-color: #44ff44'  # Green: under budget
    return ''

st.dataframe(cost_comparison, use_container_width=True)
```

#### Step 3.4: Add Decision Summary
```python
# Location: frontend/app.py

st.write("### Recommendation")

top_vendor = ranked[0]
reason = top_vendor['overall_justification']
confidence = (top_vendor['price_score'] + top_vendor['delivery_score'] + top_vendor['compliance_score']) / 30

st.success(f"""
🏆 **Recommended Vendor**: {top_vendor['vendor_name']}

**Score**: {top_vendor['weighted_score']:.0f}/100 ({confidence:.0%} confidence)

**Why**:
- Price: {top_vendor['price_score']}/10 - {top_vendor['price_score_justification']}
- Delivery: {top_vendor['delivery_score']}/10 - {top_vendor['delivery_score_justification']}
- Compliance: {top_vendor['compliance_score']}/10 - {top_vendor['compliance_score_justification']}

**Cost**: ${top_vendor['total_cost_usd']:,} ({(top_vendor['total_cost_usd']/rfq['budget']*100):.0f}% of budget)
**Timeline**: {top_vendor['timeline_weeks']} weeks ({rfq['timeline_weeks']} weeks needed)
""")
```

---

## Implementation Timeline

| Priority | Task | File(s) | Effort | Impact |
|----------|------|---------|--------|--------|
| 1 | Add FieldSource table | database.py | 1 day | Enables full traceability |
| 1 | Update extractor | extractor.py, routes/vendor.py | 1 day | Captures source info |
| 1 | Add UI display | frontend/app.py | 1 day | Shows sources to users |
| 2 | Add validation layer | services/scoring.py | 0.5 day | Catches bad scores |
| 2 | Update scoring agent | agents/scoring_agent.py | 1 day | Returns justification |
| 2 | Update score storage | models/database.py, routes/analysis.py | 0.5 day | Stores reasoning |
| 3 | Review tab UI | frontend/app.py | 1 day | UX improvement |
| 3 | Comparison charts | frontend/app.py | 0.5 day | Visual clarity |
| 3 | Decision summary | frontend/app.py | 0.5 day | Business-friendly output |

**Total Effort**: ~7.5 days for complete implementation

---

## Quick Wins (Can do today)

1. **Add validation to scoring** (30 min)
   - Open `agents/scoring_agent.py`
   - Add bounds checking before returning scores
   - Warn if score doesn't match data (e.g., high score but way over budget)

2. **Display confidence in UI** (1 hour)
   - Extract `extraction_confidence` from database
   - Show colored icons: 🟢 (>90%), 🟡 (70-90%), 🔴 (<70%)
   - Add tooltips explaining each

3. **Add simple justification prompts** (2 hours)
   - Update scoring prompt to request justification
   - Parse and store in database
   - Display in results

These quick wins build user trust immediately while you build the full solutions.
