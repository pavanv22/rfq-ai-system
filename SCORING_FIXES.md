# Scoring Service - Bug Fixes Summary

## Issues Fixed

### 1. ❌ Original Error: `'<=' not supported between instances of 'NoneType' and 'int'`

**Root Cause:**
The fallback scoring function received None values from the database but used them directly in comparisons without handling None.

```python
# BROKEN:
timeline = vendor_data.get("timeline_weeks", 4)  # Returns None if key exists with None value
if timeline <= 2:  # TypeError: None <= 2
```

**Solution:**
Use Python's `or` operator to provide defaults when values are None:

```python
# FIXED:
timeline = vendor_data.get("timeline_weeks") or 4  # Returns 4 if None or missing
if timeline <= 2:  # Now works correctly
```

---

### 2. ❌ Original Error: JSON parsing errors from Ollama

**Root Cause:**
- Ollama was returning malformed JSON with missing commas
- The `clean_json` function wasn't robust enough to handle formatting issues

**Solution:**
Enhanced `clean_json` function to:
- Extract JSON from surrounding text more robustly
- Fix common JSON formatting issues (missing commas, single quotes in keys)
- Return None if no valid JSON found (to trigger fallback)

```python
def clean_json(text):
    if not text:
        return None
    
    text = text.replace("```json", "").replace("```", "").strip()
    
    # Find first { and last } to extract JSON bounds
    start_idx = text.find('{')
    end_idx = text.rfind('}')
    
    if start_idx >= 0 and end_idx > start_idx:
        json_str = text[start_idx:end_idx+1]
        
        # Fix common issues
        json_str = re.sub(r'"\s*}(\s*)"', '"},"', json_str)
        json_str = re.sub(r"'([^']*)':", r'"\1":', json_str)
        
        return json_str
    
    return None
```

---

### 3. ❌ Original Error: Ollama runner process crashes

**Impact:**
When Ollama crashes, fallback scoring is invoked. The original fallback had no error handling for None values, causing the program to crash.

**Solution:**
Added comprehensive error handling in fallback_score_from_data:
- All numeric values default to safe values if None
- All list values default to empty lists if None
- Score boundaries enforced (1-10)
- Weighted score calculated in fallback function

---

### 4. ⚠️ Data Handling - Missing and Incomplete Fields

**Issue:**
When vendors have incomplete data in the database (fields are NULL), the scoring would fail.

**Solution:**
Updated [analysis.py](analysis.py) to provide defaults when converting ORM models to dicts:

```python
vendor_dicts = [
    {
        "vendor_name": v.vendor_name or "Unknown Vendor",
        "total_cost_usd": v.total_cost_usd or 0,        # Default to 0
        "timeline_weeks": v.timeline_weeks or 4,        # Default to 4 weeks
        "scope_coverage": v.scope_coverage or [],       # Default to empty list
        "key_terms": v.key_terms or [],                 # Default to empty list
    }
    for v in vendors
]
```

---

## Files Modified

| File | Changes |
|------|---------|
| `backend/app/agents/scoring_agent.py` | - Enhanced `clean_json()` function<br>- Updated `fallback_score_from_data()` to handle None values<br>- Added bounds checking on scores (1-10)<br>- Added timeout parameter to `score_vendor()`<br>- Added weighted_score to fallback result<br>- Improved error messages |
| `backend/app/services/scoring.py` | - Added justification fields to fallback scores<br>- Improved error logging |
| `backend/app/routes/analysis.py` | - Added default values when converting vendor ORM to dict<br>- Prevents None values from being passed to scoring |

---

## Testing

All fixes have been validated with comprehensive tests:

✅ **Test 1**: Vendor with all None values → Produces valid scores  
✅ **Test 2**: Vendor with partial None values → Produces valid scores  
✅ **Test 3**: Vendor with all valid values → Produces expected scores  
✅ **Test 4**: Weighted score calculation → Valid 0-100 range  
✅ **Test 5**: None value handling → No TypeError exceptions  

---

## Error Handling Flow

```
1. API receives scoring request
   ↓
2. Try LLM scoring via Ollama
   ├─ Success? → Return LLM scores (1/10 to 10/10)
   │
   └─ Failure (JSON, timeout, crash)?
      ↓
      Use fallback with cleaned data
      ├─ Extract scores from heuristics
      ├─ Handle ALL None values gracefully
      ├─ Validate score ranges (1-10)
      ├─ Calculate weighted score (0-100)
      └─ Return fallback scores

3. Return response with scores and justifications
```

---

## Performance Impact

- **Minimal**: Fallback logic is efficient (O(1) lookups)
- **Memory**: No additional memory usage
- **Speed**: Actually faster when fallback is used (no LLM call)

---

## Known Limitations

1. **Ollama instability**: If Ollama keeps crashing, all vendors will use fallback scoring
   - **Mitigation**: Implement health check and automatic restart of Ollama service
   
2. **Heuristic-based fallback**: May not match LLM quality exactly
   - **Mitigation**: This is intentional - fallback ensures scoring continues even if LLM fails
   
3. **No score confidence metric**: Fallback scores don't indicate confidence/reliability
   - **Future enhancement**: Add confidence% field (e.g., confidence=50% for fallback)

---

## Next Steps (Recommended)

### 🔴 Priority 1: Add Score Justification Display (Criterion #7 fix)
Add these fields to scoring justifications:
```python
{
    "price_score": 8,
    "price_justification": "Cost $47K is 35% below $72K budget",
    "price_data_used": {
        "vendor_cost": 47000,
        "rfq_budget": 72000
    }
}
```

### 🟠 Priority 2: Add Ollama Health Check
Monitor Ollama availability:
```python
@app.on_event("startup")
async def startup_event():
    check_ollama_health()
```

### 🟡 Priority 3: Add Score Confidence Metrics
Distinguish between AI scores and fallback scores:
```python
{
    "price_score": 8,
    "confidence": "high",  # or "low" for fallback scores
    "method": "llama3"      # or "heuristic"
}
```

---

## Test Results Log

```
============================================================
SCORING SERVICE FIX VALIDATION TESTS
============================================================

Test 1: Vendor with all None values
  Price Score: 7 ✓
  Delivery Score: 8 ✓
  Compliance Score: 5 ✓
  ✓ PASSED

Test 2: Vendor with partial None values
  Price Score: 6 ✓
  Delivery Score: 8 ✓
  Compliance Score: 4 ✓
  ✓ PASSED

Test 3: Vendor with all valid values
  Price Score: 8 ✓
  Delivery Score: 7 ✓
  Compliance Score: 6 ✓
  ✓ PASSED

Test 4: Weighted score calculation
  Weighted Score: 71.0 ✓
  ✓ PASSED

Test 5: None value handling in comparisons
  Successfully handled None values ✓
  ✓ PASSED

============================================================
ALL TESTS PASSED ✓
============================================================
```

---

## Summary

**Before**: Scoring crashed with TypeError when encountering None values  
**After**: Scoring gracefully handles all missing data, always returns valid scores (1-10)

The system now has **robust fallback scoring** that ensures the RFQ pipeline never breaks due to data quality or Ollama availability issues.
