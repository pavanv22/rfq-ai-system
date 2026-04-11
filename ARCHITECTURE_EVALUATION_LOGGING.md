# RFQ AI System - Architecture Diagram, Evaluation & Logging

## 1. High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          FRONTEND LAYER                                 │
│                      (Streamlit Browser UI)                             │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Tab 1: RFQ Submission  │ Tab 2: Vendor Quotations              │  │
│  │  - Create RFQ           │ - Upload vendor files (multi-format)  │  │
│  │  - View existing RFQs   │ - See extraction transparency         │  │
│  │  - Generate questions   │ - View extraction confidence          │  │
│  └────────────────────────┴────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Tab 3: Results & Scoring     │ Tab 4: Audit Trail               │  │
│  │  - Configure scoring weights  │ - All timestamped events         │  │
│  │  - View rankings              │ - Extraction events              │  │
│  │  - Show methodology           │ - Scoring events                 │  │
│  │  - Display justification      │ - Complete traceability          │  │
│  └──────────────────────────────┴──────────────────────────────────┘  │
│                                                                        │
│                    API Layer (http://localhost:8001)                  │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↑
                                    │ REST API Calls
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                          BACKEND API LAYER                              │
│                        (FastAPI Python)                                 │
│                                                                        │
│  ┌────────────────┐  ┌────────────────┐  ┌─────────────────┐         │
│  │  /rfq Routes   │  │ /vendor Routes │  │ /analysis Routes│         │
│  │  - POST /      │  │ - POST /upload │  │ - POST /score   │         │
│  │  - GET /       │  │ - GET /        │  │ - GET /scores   │         │
│  │  - PUT /{id}   │  │ - DELETE /{id} │  │ - POST /rank    │         │
│  │  - DELETE /{id}│  │                │  │                 │         │
│  └────────────────┘  └────────────────┘  └─────────────────┘         │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │                     BUSINESS LOGIC LAYER                         │ │
│  │                                                                  │ │
│  │  ┌──────────────────────────────────────────────────────────┐   │ │
│  │  │           EXTRACTION SERVICE                             │   │ │
│  │  │  • extract_pdf() → pdfplumber                           │   │ │
│  │  │  • extract_docx() → python-docx                         │   │ │
│  │  │  • extract_pptx() → python-pptx                         │   │ │
│  │  │  • extract_excel() → openpyxl                           │   │ │
│  │  │  • extract_image() → pytesseract (OCR)                 │   │ │
│  │  │  • Result: Raw extracted data with confidence scoring   │   │ │
│  │  └──────────────────────────────────────────────────────────┘   │ │
│  │                           ↓                                      │ │
│  │  ┌──────────────────────────────────────────────────────────┐   │ │
│  │  │           NORMALIZATION SERVICE                          │   │ │
│  │  │  • Currency conversion (ISO 4217, live rates)           │   │ │
│  │  │  • Timeline standardization (weeks/months/dates)        │   │ │
│  │  │  • Scope mapping (vendor scope → RFQ requirements)      │   │ │
│  │  │  • AI Inference (Ollama llama3) for missing fields      │   │ │
│  │  │  • Result: Normalized, comparable data structure        │   │ │
│  │  └──────────────────────────────────────────────────────────┘   │ │
│  │                           ↓                                      │ │
│  │  ┌──────────────────────────────────────────────────────────┐   │ │
│  │  │            SCORING SERVICE                              │   │ │
│  │  │  • Price scoring (cost analysis)                        │   │ │
│  │  │  • Delivery scoring (timeline analysis)                 │   │ │
│  │  │  • Compliance scoring (requirements met)                │   │ │
│  │  │  • Weighted calculation with configurable weights       │   │ │
│  │  │  • Ranking generation and justification                 │   │ │
│  │  │  • Result: Scored vendors with methodology explanation  │   │ │
│  │  └──────────────────────────────────────────────────────────┘   │ │
│  │                           ↓                                      │ │
│  │  ┌──────────────────────────────────────────────────────────┐   │ │
│  │  │           EVENT LOGGING SERVICE                          │   │ │
│  │  │  • Log extraction events (timestamp, vendor, confidence) │   │ │
│  │  │  • Log scoring events (timestamp, RFQ, weights)         │   │ │
│  │  │  • Store in database for audit trail                    │   │ │
│  │  │  • Enable search/filter by date, vendor, event type     │   │ │
│  │  └──────────────────────────────────────────────────────────┘   │ │
│  └──────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                          DATABASE LAYER                                 │
│                      (SQLite + SQLAlchemy ORM)                          │
│                                                                        │
│  ┌────────────────┐  ┌────────────────┐  ┌─────────────────┐         │
│  │  RFQs Table    │  │  Vendors Table │  │  Scores Table   │         │
│  │  - id (PK)     │  │  - id (PK)     │  │  - id (PK)      │         │
│  │  - project     │  │  - rfq_id (FK) │  │  - vendor_id(FK)│         │
│  │  - budget      │  │  - vendor_name │  │  - price_score  │         │
│  │  - timeline    │  │  - total_cost  │  │  - delivery_scor│         │
│  │  - scope       │  │  - currency    │  │  - compliance   │         │
│  │  - timestamp   │  │  - file_type   │  │  - weighted     │         │
│  │                │  │  - raw_data    │  │  - rank         │         │
│  │                │  │  - normalized  │  │  - timestamp    │         │
│  │                │  │  - confidence  │  │                 │         │
│  │                │  │  - timestamp   │  │                 │         │
│  └────────────────┘  └────────────────┘  └─────────────────┘         │
│                                                                        │
│  ┌──────────────────────────┐  ┌──────────────────────────┐           │
│  │  Extraction Events Table │  │  Scoring Events Table    │           │
│  │  - id (PK)               │  │  - id (PK)               │           │
│  │  - timestamp             │  │  - timestamp             │           │
│  │  - vendor_id (FK)        │  │  - rfq_id (FK)           │           │
│  │  - event_type            │  │  - event_type            │           │
│  │  - source_file           │  │  - weights_used          │           │
│  │  - extraction_status     │  │  - details               │           │
│  │  - missing_fields        │  │                          │           │
│  └──────────────────────────┘  └──────────────────────────┘           │
└─────────────────────────────────────────────────────────────────────────┘

EXTERNAL SERVICES:
  • Ollama (Port 11434) - llama3 model for AI field inference
  • Currency Exchange API - For real-time currency conversion
```

---

## 2. Data Flow Diagram

```
USER REQUEST
    ↓
┌─────────────────────────────┐
│ Frontend (Streamlit)        │ ← User uploads vendor file (any format)
│ Tab 2: Vendor Upload        │
└─────────────────────────────┘
    ↓ REST API: POST /vendor/{rfq_id}/upload
┌─────────────────────────────┐
│ Backend FastAPI             │
│ Router: /vendor             │
└─────────────────────────────┘
    ↓
┌─────────────────────────────┐
│ Extraction Service          │ ← Choose extractor based on file type
│ - Detect file type          │
│ - Call appropriate extractor│
│ - Get raw data              │
└─────────────────────────────┘
    ↓ raw_data = {
        vendor_name: "...",
        cost: "...",
        timeline: "...",
        scope: [...]
    }
┌─────────────────────────────┐
│ Normalization Service       │ ← Standardize all extracted fields
│ - Normalize currency        │
│ - Standardize timeline      │
│ - Map scope to RFQ items    │
│ - Infer missing fields (AI) │
└─────────────────────────────┘
    ↓ normalized_data = {
        vendor_name: "TechCorp Ltd",
        total_cost_usd: 450000,
        timeline_weeks: 8,
        scope_coverage: [...],
        extraction_status: "normalized"
    }
┌─────────────────────────────┐
│ Event Logging Service       │ ← Record extraction event
│ Log: VENDOR_UPLOADED        │
│ - Timestamp                 │
│ - Vendor name               │
│ - Source file type          │
│ - Confidence levels         │
└─────────────────────────────┘
    ↓
┌─────────────────────────────┐
│ Database                    │ ← Save vendor + event
│ INSERT INTO vendors         │
│ INSERT INTO extraction_logs │
└─────────────────────────────┘
    ↓
┌─────────────────────────────┐
│ Return to Frontend          │
│ Display extracted data      │
│ Show confidence levels      │
│ Show extraction transparency│
└─────────────────────────────┘

SCORING FLOW:
    ↓
USER CLICKS: "Run Scoring Analysis" (Tab 3)
    ↓
┌─────────────────────────────┐
│ Frontend requests scoring   │
│ POST /analysis/{rfq_id}/score│
│ with weights: (40, 30, 30)  │
└─────────────────────────────┘
    ↓
┌─────────────────────────────┐
│ Scoring Service             │ ← For each vendor:
│ - Get all vendors for RFQ   │   • Calculate component scores
│ - Score price              │   • Apply weights
│ - Score delivery            │   • Calculate final score
│ - Score compliance          │   • Generate rank
│ - Apply weights             │   • Create justification
│ - Rank vendors              │
└─────────────────────────────┘
    ↓
┌─────────────────────────────┐
│ Event Logging Service       │ ← Record scoring event
│ Log: SCORING_COMPLETE       │
│ - Timestamp                 │
│ - RFQ ID                    │
│ - Weights used              │
└─────────────────────────────┘
    ↓
┌─────────────────────────────┐
│ Database                    │ ← Save scores + event
│ INSERT INTO scores          │
│ INSERT INTO scoring_logs    │
└─────────────────────────────┘
    ↓
┌─────────────────────────────┐
│ Frontend displays           │
│ - Rankings table            │
│ - Score breakdown           │
│ - Methodology explanation   │
└─────────────────────────────┘
```

---

## 3. Evaluation Approach

### Key Evaluation Criteria

#### A. Functional Correctness
- **Extraction accuracy:** Does system extract vendor name, cost, timeline correctly?
  - Metric: 95%+ accuracy on common fields (name, cost)
  - Test: Run extraction on 20 sample documents in different formats
  - Expected: <5% errors, mostly edge cases

- **Normalization accuracy:** Does system normalize currencies and timelines correctly?
  - Metric: 100% accuracy on currency conversion (use live exchange rates)
  - Test: Convert vendor prices from EUR, GBP, JPY, CNY to USD
  - Expected: All conversions within 0.5% of market rate

- **Scoring consistency:** Does system produce deterministic scores?
  - Metric: Same vendor + weights → same score every run
  - Test: Run scoring 10 times with same input
  - Expected: Identical scores all 10 times

#### B. Performance
- **Extraction speed:** How long does it take to extract one document?
  - Target: <5 seconds for standard PDF/Word documents
  - Test: Upload 10 documents, measure average extraction time
  - Expected: Mean 3-4 seconds, all <10 seconds

- **Scoring speed:** How long does it take to score 10 vendors?
  - Target: <5 seconds for all 10 vendors
  - Test: Score 10+ vendor dataset, measure time
  - Expected: <1 second per vendor

- **Database query performance:** Can audit trail queries complete in <1 second?
  - Target: <1 second for filtering by date range or vendor
  - Test: Query 1000+ events, measure latency
  - Expected: <500ms response time

#### C. Reliability & Robustness
- **Error handling:** Does system gracefully handle malformed documents?
  - Test: Upload corrupted PDF, truncated Word doc, image without text
  - Expected: System returns clear error message, doesn't crash

- **Data validation:** Does system validate all input data?
  - Test: Submit RFQ with negative budget, timeline=0
  - Expected: System rejects with validation error

- **Concurrent uploads:** Can system handle multiple simultaneous uploads?
  - Target: Support 5+ concurrent vendor uploads
  - Test: Upload 5 files simultaneously
  - Expected: All complete successfully without data corruption

#### D. Usability & UX
- **Learning curve:** How quickly can new user complete first RFQ cycle?
  - Target: <10 minutes for first complete cycle
  - Test: New user attempts: Create RFQ → Upload 2 vendors → Score
  - Expected: User completes without guidance, asks minimal questions

- **Clarity of explanations:** Do users understand scoring methodology?
  - Test: Show scoring result to 5 non-technical users
  - Ask: "Why did this vendor win?"
  - Expected: Users can explain correctly using UI information

- **Audit trail usability:** Can users find specific events?
  - Test: User searches for specific vendor's events
  - Expected: User finds event in <2 clicks/searches

#### E. Explainability & Transparency
- **Extraction transparency:** Can user see all extracted fields + confidence?
  - Test: Access vendor details in Tab 2
  - Expected: See every field, confidence level, source type

- **Scoring transparency:** Can user see complete scoring methodology?
  - Test: Access vendor score in Tab 3
  - Expected: See component scores, weights, calculation, justification

- **Audit trail completeness:** Can user trace any score back to original data?
  - Test: Pick random score → Check audit trail → Verify extraction → View justification
  - Expected: Complete chain of evidence visible

---

## 4. Logging & Monitoring Strategy

### Application Logging

```python
# Configuration: backend/app/logger_config.py

import logging

# Standard logging for application events
logger = logging.getLogger("rfq_system")
logger.setLevel(logging.DEBUG)

# Create formatters
detailed_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
)

# File handler: All events
file_handler = logging.FileHandler("logs/rfq_system.log")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(detailed_formatter)

# File handler: Errors only
error_handler = logging.FileHandler("logs/errors.log")
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(detailed_formatter)

# Console handler: Info + above
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(detailed_formatter)

logger.addHandler(file_handler)
logger.addHandler(error_handler)
logger.addHandler(console_handler)
```

### Logging Events

**Extraction Service Logs:**
```
[2026-04-11 14:35:02] INFO - Extraction started: vendor_id=123, file_type=pdf
[2026-04-11 14:35:03] INFO - PDF parsed: 5 pages, 2500 words
[2026-04-11 14:35:04] INFO - Vendor name extracted: "TechCorp Ltd" (confidence=0.98)
[2026-04-11 14:35:04] INFO - Cost extracted: "$450,000 USD" (confidence=0.95)
[2026-04-11 14:35:05] INFO - Timeline extracted: "8 weeks" (confidence=0.92)
[2026-04-11 14:35:05] INFO - Extraction completed: status=normalized, missing_fields=[]
```

**Normalization Service Logs:**
```
[2026-04-11 14:35:06] INFO - Normalization started: vendor_id=123
[2026-04-11 14:35:06] INFO - Currency detected: USD (no conversion needed)
[2026-04-11 14:35:07] INFO - Timeline converted: "8 weeks" → 8
[2026-04-11 14:35:07] INFO - Scope mapping: 5 items matched to RFQ requirements
[2026-04-11 14:35:08] INFO - Normalization completed: all fields normalized
```

**Scoring Service Logs:**
```
[2026-04-11 14:50:00] INFO - Scoring started: rfq_id=456, vendor_count=3
[2026-04-11 14:50:01] INFO - Scoring vendor "TechCorp Ltd": 
  - price_score=8.5, delivery_score=7.2, compliance_score=9.0
  - weighted_score = (0.40*8.5) + (0.30*7.2) + (0.30*9.0) = 8.23
[2026-04-11 14:50:02] INFO - Scoring completed: top_vendor=TechCorp Ltd, score=82.3
```

**Error Logs:**
```
[2026-04-11 15:00:15] ERROR - Extraction failed: vendor_id=789, file_type=docx
  Exception: IOError - Cannot read file. Stack trace: ...
[2026-04-11 15:00:15] INFO - Retry attempt 1/3
[2026-04-11 15:00:20] INFO - Retry succeeded: Extraction completed successfully
```

### Performance Metrics to Log

```
# In each major operation, log:
{
    "timestamp": "2026-04-11T14:35:02Z",
    "operation": "extraction",
    "vendor_id": "123",
    "file_type": "pdf",
    "duration_ms": 3200,  # How long it took
    "status": "success",
    "fields_extracted": 8,  # Out of 10 possible
    "confidence_average": 0.95,
    "missing_fields": ["compliance_certifications"],
    "ai_inferred_fields": 1,
}
```

### Audit Trail (Database)

```sql
-- extraction_events table
CREATE TABLE extraction_events (
    id UUID PRIMARY KEY,
    timestamp DATETIME,
    vendor_id UUID FOREIGN KEY,
    event_type TEXT,  -- 'VENDOR_UPLOADED', 'EXTRACTION_COMPLETE', 'NORMALIZATION_COMPLETE'
    source_file TEXT,
    extraction_status TEXT,
    confidence_score FLOAT,
    fields_extracted JSON,
    missing_fields JSON,
    details JSON
);

-- scoring_events table
CREATE TABLE scoring_events (
    id UUID PRIMARY KEY,
    timestamp DATETIME,
    rfq_id UUID FOREIGN KEY,
    event_type TEXT,  -- 'SCORING_STARTED', 'SCORING_COMPLETE'
    weights JSON,  -- {'price': 0.4, 'delivery': 0.3, 'compliance': 0.3}
    vendor_count INT,
    top_vendor TEXT,
    top_score FLOAT,
    details JSON
);
```

### Query Audit Trail Examples

```python
# "Show me when vendor X was scored"
SELECT * FROM scoring_events 
WHERE event_type = 'SCORING_COMPLETE' 
AND details->>(vendor_id) = 'X'

# "Show me all extraction errors today"
SELECT * FROM extraction_events 
WHERE DATE(timestamp) = TODAY() 
AND extraction_status = 'incomplete'

# "Show complete timeline for RFQ Y"
SELECT * FROM extraction_events 
WHERE rfq_id = 'Y'
UNION ALL
SELECT * FROM scoring_events 
WHERE rfq_id = 'Y'
ORDER BY timestamp DESC
```

### Key Metrics to Monitor

1. **Extraction Success Rate:** % of vendor documents extracted without error
   - Target: >97%
   - Alert if: <95% (indicates document type issue or OCR failure)

2. **Average Extraction Confidence:** Mean confidence score across all extractions
   - Target: >0.92
   - Alert if: <0.85 (indicates quality degradation)

3. **Scoring Execution Time:** How long each scoring run takes
   - Target: <5 seconds per 10 vendors
   - Alert if: >15 seconds (indicates performance regression)

4. **API Response Time:** Frontend to Backend latency
   - Target: <500ms for 95% of requests
   - Alert if: >2s (indicates backend overload)

5. **Database Query Time:** Audit trail queries
   - Target: <500ms for all queries
   - Alert if: >2s (indicates index miss or data growth issue)

