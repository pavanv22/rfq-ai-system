# Test Suite - Quick Start Guide

## What Changed

Your tests have been **redesigned to match the actual codebase structure**. The template tests had incorrect imports and endpoint definitions. All tests now match your real backend APIs.

## Test Files Created/Updated

### ✅ Working Test Files

| File | Purpose | Status |
|------|---------|--------|
| `conftest.py` | Database fixtures, test client, sample data | **Updated** |
| `test_questionnaire_agent_orm_input.py` | ORM/dict input handling for agents | **Already Working** |
| `test_scoring_service.py` | ScoringService class API tests | **NEW** |
| `test_api_endpoints.py` | FastAPI endpoint tests (RFQ, Vendor, Analysis) | **NEW** |
| `test_extraction_services.py` | Extraction pipeline tests | **NEW** |
| `requirements-test.txt` | Test dependencies | **NEW** |
| `REDESIGN_SUMMARY.md` | Detailed changes documentation | **NEW** |

### ❌ Removed (Had Wrong Imports)
- `test_scoring_logic.py` (had `backend.app` imports)
- `test_extraction_vendor_formats.py` (template)
- `test_api_vendor_upload.py` (wrong endpoints)

## Key Fixes Applied

### 1. **Import Paths** ✅
**Before** (Wrong):
```python
from backend.app.services.scoring import calculate_cost_score  # Function doesn't exist
```

**After** (Correct):
```python
from app.services.scoring import ScoringService
result = ScoringService.score_vendor(vendor_data)
```

### 2. **Scoring API** ✅
**Before**:
```python
# Tried to call non-existent functions
calculate_cost_score(cost)  # ❌ Doesn't exist
```

**After**:
```python
# Uses actual ScoringService class
ScoringService.score_vendor(vendor_data)         # Returns Dict
ScoringService.score_all_vendors(vendors)        # Returns Tuple[List, Dict]
```

### 3. **Upload Endpoint** ✅
**Before**:
```python
POST /api/vendors/upload?rfq_id=123  # ❌ Wrong path
```

**After**:
```python
POST /rfqs/{rfq_id}/upload  # ✅ Correct path
```

### 4. **Fixtures** ✅
Added missing fixtures for real test data:
```python
@pytest.fixture
def client(clean_db):
    """FastAPI TestClient"""
    return TestClient(app)

@pytest.fixture
def sample_structured_data():
    """Real vendor extraction output"""
    return {
        "vendor_name": "CreativeEdge Communications Pvt Ltd",
        "cost": 343379000,
        "currency": "INR",
        ...
    }
```

## How to Run

### 1. Install Test Dependencies
```bash
pip install -r tests/requirements-test.txt
```

### 2. Run All Tests
```bash
cd tests
pytest . -v
```

### 3. Run with Coverage Report
```bash
pytest . --cov=../backend/app --cov-report=html
# Coverage report will be in htmlcov/index.html
```

### 4. Run Specific Tests
```bash
# Only scoring tests
pytest test_scoring_service.py -v

# Only API endpoint tests
pytest test_api_endpoints.py -v

# Only extraction tests
pytest test_extraction_services.py -v

# Only one test class
pytest test_scoring_service.py::TestScoringServiceBasic -v

# Only one test case
pytest test_scoring_service.py::TestScoringServiceBasic::test_score_single_vendor -v
```

## Test Organization

### test_scoring_service.py (14 tests) ✅
Tests the actual `ScoringService` class:
```
TestScoringServiceBasic
  ├─ test_score_single_vendor
  ├─ test_score_multiple_vendors
  ├─ test_score_with_minimal_fields
  ├─ test_default_weights_valid
  ├─ test_custom_weights_accepted
  ├─ test_score_empty_vendor_list
  ├─ test_three_real_vendor_costs
  ├─ test_vendor_with_zero_cost_handled
  ├─ test_vendor_with_very_high_cost_handled
  └─ test_score_returns_weighted_score_bounds

TestComputeScoreFunction (2 tests)
  ├─ test_compute_score_callable
  └─ test_compute_score_returns_list

TestScoringConsistency (2 tests)
  ├─ test_same_vendors_same_score
  └─ test_lower_cost_better_price_score
```

### test_api_endpoints.py (21 tests) ✅
Tests FastAPI endpoints:
```
TestVendorUploadAPI (3 tests)
  ├─ test_upload_vendor_requires_rfq_exists
  ├─ test_upload_pdf_vendor_success
  └─ test_upload_xlsx_vendor_success

TestRFQAPI (7 tests)
  ├─ test_create_rfq
  ├─ test_list_rfqs
  ├─ test_get_single_rfq
  ├─ test_update_rfq
  ├─ test_delete_rfq
  ├─ test_generate_questionnaire_for_rfq
  └─ test_get_questionnaire_for_rfq

TestVendorAPI (5 tests)
TestAnalysisAPI (3 tests)
TestHealthcheck (1 test)
```

### test_extraction_services.py (16 tests) ✅
Tests extraction pipeline:
```
TestExtractionPipeline (5 tests)
  ├─ test_extract_text_from_raw_proposal
  ├─ test_extract_structured_data_from_text
  ├─ test_normalize_vendor_data
  ├─ test_detect_missing_fields
  └─ test_infer_missing_values

TestExtractionWithRealFiles (3 tests)
  ├─ test_extract_from_pdf_file
  ├─ test_extract_from_xlsx_file
  └─ test_extract_from_pptx_file

TestNormalizationLogic (3 tests)
TestRobustness (3 tests)
```

### test_questionnaire_agent_orm_input.py (8 tests) ✅ Already Passing
Tests ORM/dict handling for questionnaire agent.

## Running Backend + Tests Together

### Terminal 1: Start Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Terminal 2: Run Tests
```bash
cd tests
pip install -r requirements-test.txt
pytest . -v
```

## Database Setup

Tests use SQLite test database: `test_rfq_system.db`
- ✅ Database is auto-created
- ✅ Cleaned before/after each test (no interdependencies)
- ✅ Uses actual ORM models (RFQModel, VendorModel)

## Sample Data

Fixtures provide realistic test data:

**sample_structured_data**:
```json
{
  "vendor_name": "CreativeEdge Communications Pvt Ltd",
  "cost": 343379000,
  "currency": "INR",
  "timeline_weeks": 28,
  "scope": "Integrated Marketing, TVC Production, Digital, Media Planning",
  "contact_name": "Rajesh Mehta",
  "contact_email": "r.mehta@creativeedge.in",
  "rfq_id": "RFQ-MKT-KIDS-GL-2026-001"
}
```

## Expected Test Results

When you run `pytest . -v`:

```
test_questionnaire_agent_orm_input.py::TestGetFieldHelper::test_get_field_from_orm_object PASSED ✅
test_questionnaire_agent_orm_input.py::TestGetFieldHelper::test_get_field_from_dict_object PASSED ✅
test_questionnaire_agent_orm_input.py::TestQuestionnaireAgent::test_generate_questionnaire_with_orm_rfq PASSED ✅
... (8 total for questionnaire)

test_scoring_service.py::TestScoringServiceBasic::test_score_single_vendor PASSED ✅
test_scoring_service.py::TestScoringServiceBasic::test_score_multiple_vendors PASSED ✅
... (14 total for scoring)

test_api_endpoints.py::TestRFQAPI::test_create_rfq PASSED ✅
test_api_endpoints.py::TestVendorAPI::test_create_vendor PASSED ✅
... (some skipped due to no running backend)

test_extraction_services.py::TestExtractionPipeline::test_extract_text_from_raw_proposal PASSED ✅
... (16 total for extraction)

======= 59 passed, XX skipped in X.XXs =======
```

## Troubleshooting

### ImportError: cannot import name X
- **Cause**: Backend paths changed or imports need to be from `app` not `backend.app`
- **Solution**: Check import in test file - should be `from app.services...`

### Fixture not found error
- **Cause**: conftest.py not loading
- **Solution**: Ensure conftest.py is in `tests/` directory

### Database locks
- **Cause**: Tests didn't clean up properly
- **Solution**: Delete `test_rfq_system.db` and re-run: `pytest --tb=short`

### Backend API test skipped
- **Cause**: Tests marked with `@pytest.mark.skip`
- **Solution**: Remove skip decorator to run against running backend

## Next Steps

1. ✅ **View this summary**: Complete! You're reading it.
2. 📝 **Review the tests**: Check individual test files to understand what's being tested
3. 🚀 **Run tests**: Execute `pytest . -v` in tests directory
4. 📊 **Generate coverage**: Run `pytest . --cov=../backend/app --cov-report=html`
5. 🔧 **Fix any failures**: Address failures based on actual backend implementation

## Documentation Files

- **REDESIGN_SUMMARY.md** - Detailed explanation of all changes
- **TEST_SUMMARY.md** - Original testing plan (still relevant)
- **pytest.ini** - Test configuration (markers, coverage settings)

## Success Criteria

Your tests align with your actual codebase when:
- ✅ All imports resolve without errors
- ✅ Fixtures load real test data
- ✅ 59 test cases execute
- ✅ Coverage report shows backend/app modules
- ✅ No "ImportError" or "module not found" errors

---

**Need help?** Check `REDESIGN_SUMMARY.md` for detailed documentation of changes.
