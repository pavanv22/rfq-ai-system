# RFQ AI System: 1-2 Page Overview

## Executive Summary

The RFQ AI System is an intelligent vendor evaluation platform that automates the request-for-quotation (RFQ) process while maintaining complete transparency and traceability. By combining multi-format document extraction, AI-powered data normalization, and explainable scoring algorithms, the system reduces vendor evaluation time from days to hours while improving decision defensibility through complete auditability.

---

## Problem Statement

**Traditional RFQ processes suffer from three critical challenges:**

1. **Format Friction:** Vendors submit quotations in different formats (PDF, Word, email attachments, spreadsheets, even photos). Procurement teams must manually standardize responses, introducing delays and errors.

2. **Lack of Transparency:** Vendor scoring algorithms are often treated as black boxes. When stakeholders ask "why did we choose vendor X?", procurement teams struggle to justify decisions with auditable evidence. This creates risk in high-value contracts.

3. **Manual Labor:** Comparing vendors across price, timeline, and compliance requires manual extraction, currency conversion, and calculation. For RFQs with 10+ vendors, this becomes extremely time-consuming and error-prone.

**Impact:** Large enterprises estimate 15-30 hours spent on manual RFQ evaluation per procurement cycle. With hundreds of RFQs annually, this represents millions in opportunity cost and carries risk of poor vendor selection due to human error.

---

## System Design (High Level)

### Architecture Overview

```
VENDOR SUBMISSIONS (Any Format)
    ↓
    ├─→ [Extraction Layer]
    │   ├─ PDF/DOCX/PPTX/XLSX extraction
    │   ├─ OCR for scanned images
    │   └─ Confidence scoring per field
    ↓
    ├─→ [Normalization Layer]
    │   ├─ Currency conversion (ISO 4217)
    │   ├─ Timeline standardization
    │   ├─ Scope mapping
    │   └─ AI-powered field inference
    ↓
    ├─→ [Storage Layer]
    │   ├─ Extracted data (raw + normalized)
    │   ├─ Extraction metadata (confidence, source)
    │   ├─ Audit trail (timestamps, operations)
    │   └─ Database: SQLite with SQLAlchemy ORM
    ↓
    ├─→ [Scoring Layer]
    │   ├─ Component scoring (price, delivery, compliance)
    │   ├─ Weighted calculation (configurable weights)
    │   ├─ Ranking generation
    │   └─ Explainability metadata (score breakdown)
    ↓
    └─→ [Frontend Layer - Streamlit]
        ├─ Tab 1: RFQ creation & management
        ├─ Tab 2: Vendor upload with extraction transparency
        ├─ Tab 3: Scoring with methodology display
        └─ Tab 4: Audit trail for complete traceability
```

### Technology Stack

- **Backend:** FastAPI (Python) - RESTful API on port 8001
- **Frontend:** Streamlit - Interactive web UI
- **Database:** SQLite with SQLAlchemy ORM
- **Extraction:** pdfplumber (PDF), python-docx (Word), python-pptx (PowerPoint), openpyxl (Excel), pytesseract (OCR)
- **AI/LLM:** Ollama (llama3 model) for intelligent field inference and scoring
- **Deployment:** Single-server architecture suitable for enterprise on-premises

---

## Key Assumptions

1. **Vendor data follows patterns:** Most RFQs contain consistent fields (vendor name, pricing, timeline). Vendors may use different terminology or formats, but the semantic meaning is consistent.

2. **AI inference improves over time:** The system uses Ollama for field inference on incomplete data. As the system scores more vendors, it learns which inferred fields lead to good decisions.

3. **Procurement teams want transparency:** Stakeholders prioritize defensible decisions over pure automation. They'll accept slightly longer processing time if it means auditability.

4. **Single-server deployment is sufficient:** System is designed for a single organization running 100-1000 RFQs annually. Scaling to multi-tenant SaaS would require architectural changes.

5. **Vendor data is partially structured:** While vendors provide quotations in different formats, the core information (name, price, timeline) is always present. System will struggle with truly unstructured narratives.

---

## Key Features

### 1. Multi-Format Extraction
- Automatically handles PDF, Word, PowerPoint, Excel, PNG, JPG, TXT
- OC capability for scanned documents
- Confidence scoring for each extracted field
- Fallback logic for missing or ambiguous data

### 2. AI-Powered Normalization
- **Currency conversion:** Automatically detects currency and converts to target (default USD) using live rates
- **Timeline standardization:** Converts "3 months", "12 weeks", "Q2 2026" to consistent format
- **Scope mapping:** Normalizes vendor-provided scope to RFQ requirements
- **Intelligent inference:** Uses Ollama to infer missing fields based on vendor context

### 3. Explainable Scoring
- Component scoring: Price (1-10), Delivery (1-10), Compliance (1-10)
- Configurable weights: Default 40% price, 30% delivery, 30% compliance
- Transparent calculation: Shows exact mathematical breakdown
- Methodology explanation: Users see how scores relate to RFQ requirements

### 4. Complete Audit Trail
- Timestamped events: RFQ creation, vendor uploads, extractions, scoring runs
- Immutable history: All events recorded in database
- Searchable log: Find any operation by date, vendor, or event type
- Defensibility: Six months later, justify decisions with complete evidence

### 5. User-Friendly Interface
- Four-tab workflow: Logical progression from RFQ → Vendors → Scoring → Audit
- Extraction transparency: See what was extracted, confidence levels, sources
- Scoring visualization: Charts, tables, rankings
- Real-time recalculation: Change weights and see new rankings instantly

---

## What We Would Improve

### Short-term (1-2 months)
1. **Mobile-responsive design:** Streamlit defaults aren't mobile-friendly; rebuild UI for tablets/phones
2. **Export capabilities:** Generate PDF reports of RFQ results with scoring justification
3. **Advanced filtering:** "Show me vendors under $400K with faster than 10-week delivery"
4. **Batch operations:** Upload 10+ vendor documents simultaneously

### Medium-term (3-6 months)
1. **Real-time collaboration:** Multiple procurement teams working on same RFQ simultaneously
2. **ML-powered scoring:** Learn which vendor selections led to successful past projects; update weights accordingly
3. **Vendor database integration:** Import known vendors, auto-populate fields from previous RFQs
4. **Scenario analysis:** "What if we weight compliance at 50%?" See alternative rankings instantly without re-scoring
5. **Advanced compliance checking:** Connect to compliance databases (ISO registry, certifications); auto-verify vendor claims

### Long-term (6+ months)
1. **Mobile app:** iOS/Android apps for on-the-go RFQ management
2. **Multi-language support:** Extract and score vendors in different languages; translate for comparison
3. **Supplier relationship management (SRM) integration:** Sync scoring data with ERP/procurement systems
4. **Predictive analytics:** Predict which vendors will deliver on time based on historical patterns
5. **API marketplace:** Third-party integrations (Coupa, Ariba, etc.)
6. **SaaS deployment:** Multi-tenant cloud version for managed vendors

---

## Success Metrics

- **Time Savings:** Reduce RFQ evaluation time from 24 hours to <2 hours per cycle
- **Accuracy:** Eliminate data entry errors (target: 99% accuracy vs. 85% manual)
- **Defensibility:** 100% of scoring decisions auditable with timestamp + methodology
- **User Adoption:** Procurement teams use system for >80% of RFQs within 6 months
- **Vendor Satisfaction:** Reduce vendor questions about scoring rationale (target: 50% reduction)

---

## Conclusion

The RFQ AI System addresses a real pain point in procurement: the tedious, error-prone, non-transparent process of vendor evaluation. By combining intelligent extraction, AI-powered normalization, and explainable scoring with complete auditability, it transforms vendor evaluation into a fast, transparent, defensible process that benefits procurement teams, vendors, and stakeholders alike.

The system is production-ready today for organizations with 100-1,000 annual RFQs. Future enhancements will extend capability for larger enterprises with more complex scoring requirements.

