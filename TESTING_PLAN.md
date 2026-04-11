# RFQ-AI System Automated Testing Plan

## Overview

This document defines automated tests for the RFQ extraction, vendor parsing, scoring, and questionnaire generation pipeline. Tests are organized by functional area with specific test cases, expected outcomes, and validation criteria.

**Test Data**: Three vendor proposals in different formats (PDF, PPTX, Excel) from the RFQ-MKT-KIDS-GL-2026-001 submission.

---

## 1. Unit Tests: Extraction Agent

### Test Suite: `test_extraction_agent.py`

#### 1.1 PDF Extraction (CreativeEdge Communications)

**Test Case**: `test_extract_vendor_from_pdf`
- **Input**: `Vendor1_CreativeEdge_Proposal.pdf`
- **Expected Outputs**:
  - Vendor Name: "CreativeEdge Communications Pvt. Ltd."
  - Cost: 3,43,37,900 INR (or 3.43 Crore)
  - Timeline: 28 weeks (extracted from milestone table: May 5, 2026 - Oct 26, 2026)
  - Scope: "Integrated Marketing, TVC Production, Digital, Media Planning"
  - Contact: "Rajesh Mehta"
  - RFQ ID: "RFQ-MKT-KIDS-GL-2026-001"
- **Validation**:
  - Vendor name extracted correctly (not just agency name)
  - Cost in INR format (including Crore notation)
  - Timeline in weeks calculated from dates
  - Scope summarized from 8 lots
  - All fields non-empty and trimmed

**Test Case**: `test_extract_nested_pricing_from_pdf`
- **Input**: PDF pricing structure (Section A-D breakdown)
- **Expected Output**: 
  - Aggregate 2,74,05,000 (agency fees) + 49,32,900 (GST 18%) + 20,00,000 (OOP)
  - Match header total: 3,43,37,900
- **Validation**: Nested table extraction and arithmetic validation

**Test Case**: `test_extract_multi_currency_proposal`
- **Input**: Pricing sections with both INR and USD
- **Expected Output**: 
  - Primary currency: INR 3,43,37,900
  - Secondary reference: USD 41,12,071 (recognized and stored)
- **Validation**: Multi-currency detection and preference logic

#### 1.2 PPTX Extraction (MediaPulse)

**Test Case**: `test_extract_vendor_from_pptx`
- **Input**: `Vendor2_MediaPulse_Proposal.pptx`
- **Expected Outputs**:
  - Vendor Name: "MediaPulse"
  - Cost: 2,43,08,000 INR
  - Timeline: 12 months (or ~52 weeks)
  - Status: Slide-based format (text extraction from slides)
- **Validation**:
  - Text extraction from presentation slides
  - Vendor name from title slide
  - Cost from pricing slide
  - Timeline from delivery slide

**Test Case**: `test_extract_fallback_for_pptx`
- **Input**: PPTX missing standard fields
- **Expected Output**:
  - Graceful degradation: log warning and return partial data
  - Fields attempted but missing marked as null
- **Validation**: Robust error handling without crash

#### 1.3 Excel Extraction (BrandSpark)

**Test Case**: `test_extract_vendor_from_excel`
- **Input**: `Vendor3_BrandSpark_Quotation.xlsx`
- **Expected Outputs**:
  - Vendor Name: "BrandSpark"
  - Cost: 2,85,57,000 INR
  - Timeline: 12 months (or ~52 weeks)
  - Row-based pricing structure parsed
- **Validation**:
  - Spreadsheet row iteration and cell value extraction
  - Numeric formatting (currency cells converted to float)
  - Timeline duration cells parsed

**Test Case**: `test_extract_line_items_from_excel`
- **Input**: Excel sheet with itemized costs
- **Expected Output**:
  - Line items array: [{"desc": "...", "cost": X, "unit": "..."}, ...]
  - Sum of line items matches total cost
- **Validation**: Row aggregation and sum verification

---

## 2. Unit Tests: Normalization Service

### Test Suite: `test_normalization_service.py`

#### 2.1 Cost Normalization

**Test Case**: `test_normalize_cost_inr_crore_notation`
- **Input**: "3,43,37,900", "180 Crore", "INR 3.43 Cr"
- **Expected Output**: 343379000.0 (standardized float in smallest unit)
- **Validation**: All variants normalize to same value ±0.01

**Test Case**: `test_normalize_cost_with_currency_symbol`
- **Input**: "₹ 3,43,37,900", "INR 343379000", "USD 41,12,071"
- **Expected Output**: `{value: 343379000, currency: "INR"}` or `{value: 4112071, currency: "USD"}`
- **Validation**: Currency detected and stored separately

**Test Case**: `test_normalize_cost_with_tax_breakdown`
- **Input**: Nested structure: `{subtotal: 2740500, gst: 493290, oop: 2000000}`
- **Expected Output**: 3433790 (summed total)
- **Validation**: Arithmetic verification

#### 2.2 Timeline Normalization

**Test Case**: `test_normalize_timeline_weeks_format`
- **Input**: "28w", "28 weeks", "28 WEEKS"
- **Expected Output**: `{value: 28, unit: "weeks"}`
- **Validation**: Case-insensitive, units normalized

**Test Case**: `test_normalize_timeline_months_format`
- **Input**: "12 months", "12m", "1 year"
- **Expected Output**: `{value: 52, unit: "weeks"}` (standardized to weeks)
- **Validation**: Cross-unit conversion (12 months ≈ 52 weeks)

**Test Case**: `test_normalize_timeline_date_range`
- **Input**: Start: "May 5, 2026", End: "Oct 26, 2026"
- **Expected Output**: `{value: 25, unit: "weeks"}` (calculated weeks between dates)
- **Validation**: Date parsing and duration calculation

#### 2.3 Vendor Name Normalization

**Test Case**: `test_normalize_vendor_name_whitespace`
- **Input**: "  CreativeEdge Communications Pvt. Ltd.  ", "CREATIVE EDGE COMMUNICATIONS"
- **Expected Output**: "CreativeEdge Communications Pvt Ltd" (trimmed, consistent casing)
- **Validation**: Whitespace removed, punctuation normalized

**Test Case**: `test_normalize_vendor_name_deduplication`
- **Input**: Same RFQ, three identical submissions with minor spelling variants
- **Expected Output**: Flagged as duplicate with score > 0.95
- **Validation**: Fuzzy matching on normalized names

---

## 3. Integration Tests: Extraction + Normalization

### Test Suite: `test_extraction_integration.py`

#### 3.1 End-to-End PDF Pipeline

**Test Case**: `test_pdf_extraction_to_normalized_vendor_record`
- **Input**: `Vendor1_CreativeEdge_Proposal.pdf`
- **Process**:
  1. Extract text from PDF
  2. Parse cost: "3,43,37,900" → 343379000.0 INR
  3. Parse timeline: "May 5 - Oct 26, 2026" → 25 weeks
  4. Extract vendor name: "CreativeEdge Communications Pvt. Ltd."
  5. Store in VendorModel with rfq_id = "RFQ-MKT-KIDS-GL-2026-001"
- **Expected Output**:
  ```json
  {
    "id": "uuid",
    "rfq_id": "RFQ-MKT-KIDS-GL-2026-001",
    "vendor_name": "CreativeEdge Communications Pvt Ltd",
    "cost": 343379000,
    "currency": "INR",
    "timeline_weeks": 28,
    "scope": "integrated marketing",
    "extracted_at": "2026-04-11T..."
  }
  ```
- **Validation**:
  - Fields match expected values within tolerance
  - Timestamps valid ISO format
  - No null mandatory fields
  - DB insert succeeds without duplication error

#### 3.2 Multi-Format Comparison

**Test Case**: `test_three_vendors_extracted_and_comparable`
- **Input**: All three vendor files
- **Process**:
  1. Extract all three vendors
  2. Normalize all costs to INR
  3. Normalize all timelines to weeks
  4. Create sortable records
- **Expected Output**:
  ```json
  [
    {"vendor": "BrandSpark", "cost": 285570000, "timeline": 52},
    {"vendor": "MediaPulse", "cost": 243080000, "timeline": 52},
    {"vendor": "CreativeEdge Communications", "cost": 343379000, "timeline": 28}
  ]
  ```
- **Validation**:
  - All three records extracted with no errors
  - Cost and timeline fields numeric and comparable
  - Sorting by cost/timeline produces consistent results

---

## 4. Unit Tests: Scoring Service

### Test Suite: `test_scoring_service.py`

#### 4.1 Cost Scoring

**Test Case**: `test_cost_score_lower_is_better`
- **Input**: Vendors with costs [2,43,08,000, 2,85,57,000, 3,43,37,900]
- **Expected Output**: 
  - MediaPulse (2.43Cr): score 100
  - BrandSpark (2.85Cr): score ~85
  - CreativeEdge (3.43Cr): score ~71
- **Validation**: Inverse linear scoring (lowest cost = highest score)

**Test Case**: `test_cost_score_with_outliers`
- **Input**: Vendor with cost 10x higher than others
- **Expected Output**: Score capped or flagged; no division by zero
- **Validation**: Robust scoring even with outliers

#### 4.2 Timeline Scoring

**Test Case**: `test_timeline_score_shorter_is_better`
- **Input**: Vendors with timelines [12m/52w, 12m/52w, 28w]
- **Expected Output**:
  - CreativeEdge (28w): score 100
  - MediaPulse/BrandSpark (52w): score ~54
- **Validation**: Shorter timeline = higher score

**Test Case**: `test_timeline_score_normalized_across_units`
- **Input**: Timelines in mixed units (weeks, months, date ranges)
- **Expected Output**: All scores comparable despite input format variants
- **Validation**: Unit normalization transparent; scores consistent

#### 4.3 Compliance Scoring (Binary)

**Test Case**: `test_compliance_score_required_fields`
- **Input**: 
  - Vendor A: Has compliance framework + child safety + claims substantiation ✓
  - Vendor B: Missing claims substantiation ✗
- **Expected Output**:
  - Vendor A: compliance_score = 100
  - Vendor B: compliance_score = 66 (2/3 items)
- **Validation**: Checklist-based scoring

#### 4.4 Weighted Score Aggregation

**Test Case**: `test_final_score_weighted_sum`
- **Input**: 
  - Cost score: 80, weight 0.4
  - Timeline score: 90, weight 0.3
  - Compliance score: 100, weight 0.3
- **Expected Output**: Final score = 0.4×80 + 0.3×90 + 0.3×100 = 89.0
- **Validation**: Arithmetic correct; weights sum to 1.0

---

## 5. API Tests: Route Integration

### Test Suite: `test_api_routes.py`

#### 5.1 Vendor Upload Endpoint

**Test Case**: `test_post_vendor_upload_pdf`
- **Method**: `POST /api/vendors/upload`
- **Input**:
  - Form data: `file=Vendor1_CreativeEdge_Proposal.pdf`
  - Query: `rfq_id=RFQ-MKT-KIDS-GL-2026-001`
- **Expected Response**:
  ```json
  {
    "status": "success",
    "vendor": {
      "id": "uuid",
      "vendor_name": "CreativeEdge Communications Pvt Ltd",
      "cost": 343379000,
      "timeline_weeks": 28
    }
  }
  ```
- **Validation**:
  - HTTP 201 Created
  - Response contains vendor ID (uuid format)
  - Cost and timeline non-null
  - DB entry confirmed

**Test Case**: `test_post_vendor_upload_duplicate_prevention`
- **Method**: `POST /api/vendors/upload` (same file, second time)
- **Expected Behavior**:
  - First upload: Creates new vendor record
  - Second upload: Updates existing vendor (same rfq_id + vendor_name)
  - Result: Single record in DB (no duplication)
- **Validation**: Count before/after = 1

**Test Case**: `test_post_vendor_upload_multiformat_batch`
- **Method**: Multiple parallel `POST /api/vendors/upload` calls
- **Input**: All three vendor files simultaneously
- **Expected Response**: All three upload successfully within 10 seconds
- **Validation**: 
  - No database locking errors
  - All three records present post-upload
  - No data corruption or partial inserts

#### 5.2 Scoring Endpoint

**Test Case**: `test_post_run_scoring`
- **Method**: `POST /api/analysis/run-scoring`
- **Input**: `{"rfq_id": "RFQ-MKT-KIDS-GL-2026-001"}`
- **Expected Response**:
  ```json
  {
    "status": "success",
    "scores": [
      {
        "vendor_name": "MediaPulse",
        "cost_score": 100,
        "timeline_score": 54,
        "compliance_score": 85,
        "final_score": 80.1
      },
      ...
    ]
  }
  ```
- **Validation**:
  - HTTP 200 OK
  - All three vendors scored
  - Scores in range [0, 100]
  - Final scores ordered descending

**Test Case**: `test_get_scores_retrieval`
- **Method**: `GET /api/analysis/scores?rfq_id=RFQ-MKT-KIDS-GL-2026-001`
- **Expected Response**: Array of vendor scores (JSON)
- **Validation**:
  - No serialization errors (Pydantic-safe dicts)
  - ISO datetime format for timestamps
  - Vendor_name included

#### 5.3 Questionnaire Generation Endpoint

**Test Case**: `test_post_generate_questions`
- **Method**: `POST /api/rfqs/{rfq_id}/generate-questions`
- **Input**: RFQ ID from CreativeEdge upload
- **Expected Response**:
  ```json
  {
    "id": "uuid",
    "rfq_id": "RFQ-MKT-KIDS-GL-2026-001",
    "questions": [
      {"question": "What is your experience...", "category": "experience", "required": true},
      ...
    ],
    "created_at": "2026-04-11T..."
  }
  ```
- **Validation**:
  - HTTP 201 Created
  - Questions array non-empty (min 4 categories)
  - Each question has 3 fields: question, category, required
  - No LLM call errors (Ollama must be running)

**Test Case**: `test_generate_questions_handles_orm_and_dict_inputs`
- **Purpose**: Verify questionnaire_agent accepts both RFQModel ORM objects and dicts
- **Input**: 
  - Scenario 1: Route passes RFQModel instance
  - Scenario 2: Route manually converts to dict; passes dict
- **Expected Output**: Both scenarios produce identical questions
- **Validation**: No "'RFQModel' object is not subscriptable" error; consistent output

---

## 6. Database Tests

### Test Suite: `test_database_integrity.py`

#### 6.1 Vendor Record Persistence

**Test Case**: `test_vendor_record_insert_and_retrieve`
- **Process**:
  1. Create Vendor record: VendorModel(rfq_id="RFQ-...", vendor_name="CreativeEdge...", cost=343379000, ...)
  2. Insert to DB
  3. Query by rfq_id + vendor_name
  4. Verify all fields match
- **Validation**: ACID compliance

#### 6.2 Duplicate Prevention

**Test Case**: `test_duplicate_vendor_update_not_insert`
- **Process**:
  1. Insert vendor V1 with (rfq_id="X", vendor_name="Y", cost=100)
  2. Attempt to insert identical vendor (cost updated to 150)
  3. Query DB: expect 1 record with cost=150 (updated)
- **Validation**: Count = 1, cost = 150

#### 6.3 Referential Integrity

**Test Case**: `test_rfq_vendor_foreign_key_constraint`
- **Process**:
  1. Create RFQ with id "ABC"
  2. Create Vendor with rfq_id="ABC"
  3. Attempt to delete RFQ
  4. Verify cascade delete removes vendor
- **Validation**: Orphaned records not possible

#### 6.4 Transaction Rollback on Error

**Test Case**: `test_rollback_on_db_exception`
- **Process**:
  1. Start transaction: Insert vendor
  2. Force exception mid-insert (e.g., invalid cost type)
  3. Verify no partial record in DB
- **Validation**: DB state unchanged after rollback

---

## 7. End-to-End Workflow Tests

### Test Suite: `test_e2e_workflows.py`

#### 7.1 Complete RFQ Submission & Scoring

**Test Case**: `test_e2e_upload_three_vendors_score_and_rank`
- **Workflow**:
  1. Create RFQ: POST /api/rfqs with title "RFQ-MKT-KIDS-GL-2026-001"
  2. Upload Vendor1 (PDF): POST /api/vendors/upload
  3. Upload Vendor2 (PPTX): POST /api/vendors/upload
  4. Upload Vendor3 (Excel): POST /api/vendors/upload
  5. Run scoring: POST /api/analysis/run-scoring
  6. List vendors: GET /api/vendors?rfq_id=...
  7. Get scores: GET /api/analysis/scores?rfq_id=...
  8. Generate questions: POST /api/rfqs/{id}/generate-questions
- **Expected Sequence**:
  - Step 1: RFQ created with status "active"
  - Step 2-4: Three vendor records inserted (no errors)
  - Step 5: Scoring completes; 3 scores computed
  - Step 6: Returns all 3 vendors sorted by cost
  - Step 7: Returns scores ordered by final_score descending
  - Step 8: Questionnaire generated with 8-12 questions
- **Validation**:
  - All HTTP responses 200/201
  - Data consistency across endpoints
  - No missing records
  - Timestamps monotonically increasing

#### 7.2 Database Cleanup Workflow

**Test Case**: `test_e2e_clear_database_and_restart`
- **Workflow**:
  1. Run test 7.1 above (populate DB)
  2. Execute clear_database.py script
  3. Query: verify DB tables empty
  4. Restart backend service
  5. Re-run test 7.1 (confirm clean start works)
- **Validation**:
  - No stale data interference
  - Service restart successful
  - Clean slate for next test run

#### 7.3 Concurrent Vendor Uploads

**Test Case**: `test_e2e_parallel_vendor_uploads_no_race_condition`
- **Workflow**:
  1. Create RFQ
  2. Launch 3 concurrent upload requests (all three vendor files simultaneously)
  3. Wait for all to complete
  4. Verify: exactly 3 vendors in DB, no partial inserts, no duplicates
- **Validation**:
  - Final vendor count = 3
  - All files extracted successfully
  - No database lock timeout errors
  - All scores computed correctly post-upload

---

## 8. Performance Tests

### Test Suite: `test_performance.py`

#### 8.1 Extraction Speed

**Test Case**: `test_pdf_extraction_performance_under_5s`
- **Input**: Vendor1_CreativeEdge_Proposal.pdf (16 pages)
- **Expected**: Extraction completes in < 5 seconds
- **Validation**: Timer assertion on extraction function

**Test Case**: `test_excel_extraction_performance_under_2s`
- **Input**: Vendor3_BrandSpark_Quotation.xlsx (multi-sheet)
- **Expected**: Extraction completes in < 2 seconds
- **Validation**: Timer assertion

#### 8.2 Scoring Speed

**Test Case**: `test_scoring_three_vendors_under_1s`
- **Input**: 3 vendors already uploaded
- **Process**: Run scoring calculation
- **Expected**: Completes in < 1 second
- **Validation**: Timer assertion

#### 8.3 API Response Time

**Test Case**: `test_api_upload_response_time_under_3s`
- **Input**: Any vendor file upload
- **Expected**: HTTP response received in < 3 seconds (including extraction + DB insert)
- **Validation**: Response time assertion

---

## 9. Error Handling & Edge Cases

### Test Suite: `test_error_handling.py`

#### 9.1 File Format Errors

**Test Case**: `test_upload_unsupported_format_rejected`
- **Input**: File with .doc (Word) extension
- **Expected Response**: HTTP 400 Bad Request with message "Unsupported file format. Accepted: PDF, PPTX, XLSX"
- **Validation**: Graceful rejection

**Test Case**: `test_upload_corrupted_pdf_handled`
- **Input**: Truncated/corrupted PDF file
- **Expected**: HTTP 422 Unprocessable Entity; log error without crash
- **Validation**: Extraction fallback or error message

**Test Case**: `test_upload_missing_rfq_id_parameter`
- **Input**: POST /api/vendors/upload without rfq_id query param
- **Expected Response**: HTTP 400 Bad Request
- **Validation**: Parameter validation

#### 9.2 Data Validation Errors

**Test Case**: `test_invalid_cost_format_rejected`
- **Input**: Vendor with cost = "abc xyz" (non-numeric)
- **Expected**: HTTP 422; error message "Invalid cost format"
- **Validation**: Type validation

**Test Case**: `test_negative_cost_rejected`
- **Input**: Vendor with cost = -100000
- **Expected**: HTTP 422; error message "Cost must be positive"
- **Validation**: Business logic validation

**Test Case**: `test_timeline_zero_or_negative_rejected`
- **Input**: Vendor with timeline_weeks = 0 or -5
- **Expected**: HTTP 422; error message
- **Validation**: Business rule enforcement

#### 9.3 LLM/External Service Errors

**Test Case**: `test_questionnaire_generation_llm_unavailable`
- **Setup**: Stop Ollama service
- **Input**: POST /api/rfqs/{id}/generate-questions
- **Expected Response**: HTTP 503 Service Unavailable with message "LLM service not ready. Ensure Ollama is running on localhost:11434"
- **Validation**: Graceful degradation; informative error

**Test Case**: `test_questionnaire_generation_timeout_recovery`
- **Setup**: Configure Ollama with intentional 60s delay
- **Input**: POST /api/rfqs/{id}/generate-questions
- **Expected**: Request times out after 30s; HTTP 504 Gateway Timeout
- **Validation**: Timeout handling

---

## 10. Test Data Management

### Test Fixtures

**Location**: `tests/fixtures/`

#### Fixture Files:
```
fixtures/
├── Vendor1_CreativeEdge_Proposal.pdf
├── Vendor2_MediaPulse_Proposal.pptx
├── Vendor3_BrandSpark_Quotation.xlsx
├── corrupted_vendor.pdf (for error tests)
├── incomplete_vendor.xlsx (missing cost field)
└── test_rfq_config.json
```

#### Fixture Setup (conftest.py):
```python
@pytest.fixture(scope="function")
def clean_db():
    """Clear database before each test."""
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

@pytest.fixture
def test_rfq():
    """Create a test RFQ."""
    rfq = RFQModel(id="test-rfq-001", subject="Test RFQ")
    db.add(rfq)
    db.commit()
    return rfq

@pytest.fixture
def sample_vendor_pdf():
    """Return path to sample vendor PDF."""
    return Path(__file__).parent / "fixtures" / "Vendor1_CreativeEdge_Proposal.pdf"
```

---

## 11. Test Execution Strategy

### Local Execution (Development)

```bash
# All tests
pytest tests/ -v

# By category
pytest tests/test_extraction_agent.py -v
pytest tests/test_extraction_integration.py -v
pytest tests/test_scoring_service.py -v
pytest tests/test_api_routes.py -v
pytest tests/test_e2e_workflows.py -v

# With coverage
pytest tests/ --cov=backend/app --cov-report=html

# Specific test
pytest tests/test_api_routes.py::test_post_vendor_upload_pdf -v -s
```

### Continuous Integration (GitHub Actions / GitLab CI)

```yaml
# .github/workflows/test.yml
name: Automated Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Start Ollama (for LLM tests)
        run: docker run -d -p 11434:11434 ollama/ollama
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest tests/ --cov=backend/app --junitxml=results.xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

---

## 12. Test Metrics & Success Criteria

| Metric | Target | Threshold |
|--------|--------|----------|
| Code Coverage | 80% | Minimum 70% |
| Test Pass Rate | 100% | Maximum 2 flaky tests |
| Extraction Accuracy | 95% | Minimum 90% |
| API Response Time | < 3s | Maximum 5s |
| Database Integrity | No orphans | Zero violations |
| End-to-End Duration | < 30s | Maximum 60s |

---

## 13. Test Execution Checklist

Before each release:

- [ ] All unit tests pass (`pytest tests/test_*.py -v`)
- [ ] All integration tests pass
- [ ] All E2E tests pass
- [ ] Coverage report generated and reviewed (> 80%)
- [ ] Performance tests show acceptable times
- [ ] Database cleanup verified
- [ ] Error scenarios tested with Ollama stopped
- [ ] Concurrent upload test completed successfully
- [ ] No database orphans post-test (validation query)
- [ ] Local server restart successful

---

## 14. Appendix: Key Validation Queries

### Verify Vendor Records Inserted
```sql
SELECT COUNT(*) AS vendor_count, 
       GROUP_CONCAT(vendor_name, ', ') AS names
FROM vendors
WHERE rfq_id = 'RFQ-MKT-KIDS-GL-2026-001';
```
Expected: 3 vendors (CreativeEdge, MediaPulse, BrandSpark)

### Verify Scores Computed
```sql
SELECT vendor_name, cost_score, timeline_score, compliance_score, final_score
FROM scores
WHERE rfq_id = 'RFQ-MKT-KIDS-GL-2026-001'
ORDER BY final_score DESC;
```
Expected: 3 rows, scores in [0, 100], ordered descending

### Verify No Duplicates
```sql
SELECT vendor_name, COUNT(*) AS cnt
FROM vendors
WHERE rfq_id = 'RFQ-MKT-KIDS-GL-2026-001'
GROUP BY vendor_name
HAVING cnt > 1;
```
Expected: No rows (zero duplicates)

---

## 15. Future Enhancements

- [ ] Load testing with 100+ concurrent vendors
- [ ] Multi-RFQ workflow tests
- [ ] Contract validation tests (compare against RFQ template)
- [ ] Budget variance analysis tests
- [ ] Vendor comparison report generation tests
- [ ] Export to CSV/PDF tests
- [ ] Real Ollama integration test (or mock)
- [ ] Shadow mode testing (parallel old vs new extraction logic)

---

## Appendix A: File Manifest

### Created Test Files

```
tests/
├── conftest.py                                 # Global fixtures and setup
├── README.md                                   # Test guide and quickstart
├── test_questionnaire_agent_orm_input.py      # ORM/dict input handling
├── test_extraction_vendor_formats.py          # PDF/PPTX/Excel extraction
├── test_scoring_logic.py                      # Scoring calculations
├── test_api_vendor_upload.py                  # Upload endpoints
├── test_extraction_integration.py             # (Template for integration tests)
├── test_e2e_workflows.py                      # (Template for E2E tests)
├── test_database_integrity.py                 # (Template for DB tests)
├── test_error_handling.py                     # (Template for error tests)
├── test_performance.py                        # (Template for perf tests)
└── fixtures/
    ├── Vendor1_CreativeEdge_Proposal.pdf      # Test data
    ├── Vendor2_MediaPulse_Proposal.pptx       # Test data
    ├── Vendor3_BrandSpark_Quotation.xlsx      # Test data
    ├── corrupted_vendor.pdf                   # (To be added)
    ├── incomplete_vendor.xlsx                 # (To be added)
    └── test_rfq_config.json                   # (To be added)
```

### Configuration Files

```
project-root/
├── pytest.ini                                  # Pytest configuration
├── TESTING_PLAN.md                             # This file
├── .github/workflows/test.yml                 # (Optional CI config)
└── tests/README.md                             # Test execution guide
```

---

## Appendix B: Test Input Data Summary

| Vendor | File | Format | Cost (INR) | Timeline | Key Fields |
|--------|------|--------|------------|----------|-----------|
| CreativeEdge Communications | Vendor1_...pdf | PDF (16 pages) | 3,43,37,900 | 28w (May 5 - Oct 26, 2026) | Name, 8 lots, nested pricing, compliance framework |
| MediaPulse | Vendor2_...pptx | PowerPoint | 2,43,08,000 | 12mo (~52w) | Slides, cost, timeline |
| BrandSpark | Vendor3_...xlsx | Excel | 2,85,57,000 | 12mo (~52w) | Rows, line items, summary |

**Extraction Targets**:
- Vendor Name: Standardized, deduplicated
- Cost: Normalized to INR, numeric
- Timeline: Converted to weeks
- Scope: Extracted from documents
- Contact: Name and email if present
- RFQ ID: \"RFQ-MKT-KIDS-GL-2026-001\"

---

## Appendix C: Expected Test Results

### Successful Extraction
```json
[
  {
    \"vendor_name\": \"CreativeEdge Communications Pvt Ltd\",
    \"cost\": 343379000,
    \"currency\": \"INR\",\n    \"timeline_weeks\": 28,
    \"scope\": \"integrated marketing, tvc production, digital, compliance\",
    \"contact\": {\"name\": \"Rajesh Mehta\", \"email\": \"r.mehta@creativeedge.in\"},\n    \"rfq_id\": \"RFQ-MKT-KIDS-GL-2026-001\",\n    \"status\": \"extracted\"\n  },\n  {\"vendor_name\": \"MediaPulse\", \"cost\": 243080000, ...},\n  {\"vendor_name\": \"BrandSpark\", \"cost\": 285570000, ...}\n]\n```\n\n### Scoring Results\n```json\n[\n  {\n    \"vendor_name\": \"MediaPulse\",\n    \"cost_score\": 100,\n    \"timeline_score\": 54,\n    \"compliance_score\": 85,\n    \"final_score\": 79.7,\n    \"rank\": 1\n  },\n  {\n    \"vendor_name\": \"BrandSpark\",\n    \"cost_score\": 85,\n    \"timeline_score\": 54,\n    \"compliance_score\": 90,\n    \"final_score\": 76.2,\n    \"rank\": 2\n  },\n  {\n    \"vendor_name\": \"CreativeEdge Communications Pvt Ltd\",\n    \"cost_score\": 71,\n    \"timeline_score\": 100,\n    \"compliance_score\": 100,\n    \"final_score\": 84.3,\n    \"rank\": 1\n  }\n]\n```\n**Note**: Final scores depend on weights. Adjust COST_WEIGHT, TIMELINE_WEIGHT, COMPLIANCE_WEIGHT in scoring.py to calibrate ranking.\n\n---\n\n## Appendix D: Running Tests in Different Environments\n\n### Local Development (with IDE)\n\n**VS Code with Python extension**:\n1. Install pytest extension\n2. Open test file\n3. Click \"Run\" above test function\n4. Or press `Ctrl+Shift+D` to run all tests\n\n**PyCharm**:\n1. Right-click on tests/ folder → \"Run pytest\"\n2. Or use Ctrl+Shift+F10\n\n### Command Line (CI/CD)\n\n```bash\n# Basic\npytest tests/\n\n# With coverage\npytest tests/ --cov=backend/app --cov-report=term-missing\n\n# JUnit XML for CI systems\npytest tests/ --junitxml=test-results.xml\n\n# Verbose with markers\npytest tests/ -v -m \"not slow\"\n\n# Stop on first failure, show locals on failure\npytest tests/ -x --tb=long --showlocals\n```\n\n### Docker\n\n```dockerfile\nFROM python:3.10\nWORKDIR /app\nCOPY requirements.txt .\nRUN pip install -r requirements.txt\nCOPY . .\nCMD [\"pytest\", \"tests/\", \"--cov=backend/app\", \"--cov-report=html\"]\n```\n\n```bash\ndocker build -t rfq-tests .\ndocker run rfq-tests\n```\n\n---\n\n## Appendix E: Quick Reference: Test Commands\n\n```bash\n# All tests\npytest tests/ -v\n\n# With coverage\npytest tests/ --cov=backend/app --cov-report=html\n\n# Specific test file\npytest tests/test_questionnaire_agent_orm_input.py -v\n\n# Specific test class\npytest tests/test_questionnaire_agent_orm_input.py::TestGetFieldHelper -v\n\n# Specific test\npytest tests/test_questionnaire_agent_orm_input.py::TestGetFieldHelper::test_get_field_from_dict -v\n\n# By marker\npytest tests/ -m integration\npytest tests/ -m \"not slow\"\n\n# Show print statements\npytest tests/ -v -s\n\n# Stop on first failure\npytest tests/ -x\n\n# Show local variables on failure\npytest tests/ --tb=long --showlocals\n\n# Generate HTML report\npytest tests/ --html=report.html --cov=backend/app --cov-report=html\n\n# Collect only (show what would run)\npytest tests/ --collect-only\n\n# Filter by keyword\npytest tests/ -k \"extraction\" -v\n```
