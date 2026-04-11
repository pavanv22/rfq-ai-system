# RFQ-AI System Test Suite

## Overview

This directory contains comprehensive automated tests for the RFQ (Request for Quotation) extraction, vendor analysis, and scoring system. The test suite covers:

- **Unit Tests**: Individual functions and components in isolation
- **Integration Tests**: Multiple components working together
- **API Tests**: HTTP endpoint validation
- **End-to-End Tests**: Complete workflow from upload to scoring
- **Error Handling Tests**: Edge cases and failure scenarios
- **Performance Tests**: Response time and scalability checks

## Quick Start

### Prerequisites

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-asyncio

# Ensure backend and frontend are NOT running
# (Tests use isolated database)
```

### Run All Tests

```bash
# From project root
pytest tests/ -v

# With coverage report
pytest tests/ --cov=backend/app --cov-report=html

# Open coverage report
open htmlcov/index.html  # macOS
start htmlcov\index.html # Windows
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest tests/test_questionnaire_agent_orm_input.py -v -m unit

# Integration tests
pytest tests/test_extraction_integration.py -v -m integration

# API tests
pytest tests/test_api_vendor_upload.py -v

# End-to-end tests
pytest tests/test_e2e_workflows.py -v -m e2e

# Performance tests
pytest tests/test_performance.py -v -m performance

# Error handling tests
pytest tests/test_error_handling.py -v -m error_handling
```

### Run Single Test

```bash
# Run one specific test
pytest tests/test_questionnaire_agent_orm_input.py::TestGenerateQuestionnaireOrmInput::test_generate_questionnaire_accepts_orm_model -v

# With detailed output
pytest tests/test_questionnaire_agent_orm_input.py::TestGenerateQuestionnaireOrmInput::test_generate_questionnaire_accepts_orm_model -v -s
```

## Test Data

Three vendor proposal files are used as test data:

1. **Vendor1_CreativeEdge_Proposal.pdf** (16 pages, 3.43 Cr INR, 28 weeks)
   - Nested pricing structure (Sections A-D)
   - Milestone timeline (May 5 - Oct 26, 2026)
   - Full compliance framework

2. **Vendor2_MediaPulse_Proposal.pptx** (PowerPoint slides)
   - Cost: 2.43 Cr INR
   - Timeline: 12 months (~52 weeks)
   - Slide-based content

3. **Vendor3_BrandSpark_Quotation.xlsx** (Excel spreadsheet)
   - Cost: 2.85 Cr INR
   - Timeline: 12 months (~52 weeks)
   - Row-based line items

**Location**: `tests/fixtures/[filename]`

## Test Fixtures

Common database and data fixtures are defined in [conftest.py](conftest.py):

- `clean_db`: Provides fresh database for each test
- `db`: Database session fixture
- `test_rfq`: Pre-created test RFQ record
- `test_vendor`: Pre-created test vendor record
- `test_rfq_dict`: RFQ as dictionary (for agent testing)
- `sample_vendor_pdf/xlsx/pptx`: File path fixtures

## Key Test Files

### conftest.py
Global pytest configuration, fixtures, and shared setup/teardown logic.

### test_questionnaire_agent_orm_input.py
Tests for questionnaire generation agent accepting both ORM and dict inputs.
**Key**: Validates fix for "'RFQModel' object is not subscriptable" error.

### test_extraction_vendor_formats.py
Tests for extracting vendor data from PDF, PPTX, and Excel formats.
Validates vendor name, cost, and timeline extraction from each format.

### test_scoring_logic.py
Tests for scoring calculations (cost, timeline, compliance, weighted aggregation).
Validates score bounds, consistency, and ranking logic.

### test_api_vendor_upload.py
API endpoint tests for vendor file upload, duplicate detection, and concurrent uploads.

### test_extraction_integration.py
*(To be created)* End-to-end extraction→normalization→storage pipeline tests.

### test_e2e_workflows.py
*(To be created)* Full workflow: RFQ creation → vendor upload → scoring → questionnaire.

## Test Naming Conventions

- `test_xxx_success` or `test_xxx_valid`: Happy path / expected behavior
- `test_xxx_error` or `test_xxx_rejected`: Error handling
- `test_xxx_with_xxx`: Tests with specific conditions/data
- `test_xxx_concurrent`: Parallel execution tests
- `test_xxx_performance_xxx`: Performance/speed tests

## Debugging Tests

### Print Debug Output

```bash
# Use -s flag to show print statements
pytest tests/test_questionnaire_agent_orm_input.py -v -s
```

### Stop on First Failure

```bash
# Exit immediately on first test failure
pytest tests/ -x
```

### Drop into Debugger

```python
# In test file:
def test_something():
    import pdb; pdb.set_trace()
    # ... test code after breakpoint
```

Then run:
```bash
pytest tests/test_xxx.py -s
```

### Show Test Collection Without Running

```bash
# See what tests pytest would run
pytest tests/ --collect-only

# Specific pattern
pytest tests/ --collect-only -k "extraction"
```

## CI/CD Integration

### GitHub Actions

Test via `.github/workflows/test.yml` (if configured):

```bash
# Simulate CI environment locally
pytest tests/ --cov=backend/app --junitxml=test-results.xml
```

### Pre-commit Hook

Run tests before each commit:

```bash
# .git/hooks/pre-commit
#!/bin/bash
pytest tests/ -x --tb=short
if [ $? -ne 0 ]; then
  echo "Tests failed. Commit aborted."
  exit 1
fi
```

## Common Issues & Troubleshooting

### Issue: "sqlite3.OperationalError: database is locked"
**Cause**: Database being read by another process (backend running?)  
**Fix**: Stop backend servers before running tests
```bash
# Kill any Python processes
pkill -f "uvicorn\|streamlit"
```

### Issue: "ModuleNotFoundError: No module named 'app'"
**Cause**: PYTHONPATH not set correctly  
**Fix**: Run tests from project root:
```bash
cd /path/to/rfq-ai-system/
pytest tests/
```

### Issue: "RequestException: HTTPConnectionPool...Cannot connect to host"
**Cause**: Tests trying to contact Ollama but it's not running  
**Fix**: For LLM tests, ensure Ollama is running or use pytest marker to skip:
```bash
pytest tests/ -m "not requires_ollama"
```

### Issue: "KeyError" or "AttributeError" in fixture
**Cause**: Fixture not properly configured  
**Fix**: Check conftest.py imports and verify database initialization
```bash
pytest tests/ --fixtures | grep -A5 clean_db
```

## Performance Benchmarks

Expected test execution times:

| Test Category | Count | Duration | Target |
|---|---|---|---|
| Unit | ~20 | 1-2s | < 100ms per test |
| Integration | ~15 | 2-3s | < 200ms per test |
| API | ~10 | 3-5s | < 500ms per test |
| E2E | ~5 | 5-10s | < 2s per test |
| Performance | ~5 | 1-2s | Pass if < thresholds |
| **Total** | **~55** | **~15-25s** | **Complete in < 30s** |

## Coverage Goals

- **Overall**: 80% minimum
- **backend/app/services**: 90% minimum
- **backend/app/agents**: 85% minimum
- **backend/app/routes**: 75% minimum

View coverage report:
```bash
pytest tests/ --cov=backend/app --cov-report=html
open htmlcov/index.html
```

## Best Practices

1. **Use fixtures for setup/teardown**: Avoid code duplication
2. **Test one thing per test**: Single assertion focus
3. **Use descriptive names**: Clear intent from test name
4. **Keep tests isolated**: No dependencies between tests
5. **Mock external services**: Don't call real APIs
6. **Test error paths**: Not just happy path
7. **Clean up after tests**: Delete temp files, clear DB

## Adding New Tests

1. Create file: `tests/test_feature_name.py`
2. Import fixtures from conftest.py
3. Define test class: `class TestFeatureName:`
4. Write test methods: `def test_xxx(fixture1, fixture2):`
5. Use clear assertions: `assert result == expected`
6. Run tests: `pytest tests/test_feature_name.py -v`

Example:
```python
# tests/test_new_feature.py
import pytest

class TestNewFeature:
    def test_basic_behavior(self, clean_db):
        """Test basic feature behavior."""
        result = do_something()
        assert result == expected_value
    
    def test_error_handling(self, clean_db):
        """Test error scenario."""
        with pytest.raises(ValueError):
            do_something_invalid()
```

## Related Documentation

- See [TESTING_PLAN.md](../TESTING_PLAN.md) for detailed test specifications
- Backend routes: `backend/app/routes/`
- Extraction agents: `backend/app/agents/`
- Scoring logic: `backend/app/services/scoring.py`
