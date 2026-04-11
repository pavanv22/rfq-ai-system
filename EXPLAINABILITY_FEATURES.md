# Explainability & Traceability Features

## Overview
The RFQ AI System v2.0 frontend now includes comprehensive explainability and traceability features to ensure every insight is traceable from source data to final recommendation.

## 1. Extraction Transparency

### 1.1 Extraction Details & Traceability Panel
**Location:** Vendor Quotations Tab → Upload Section

When a vendor response is uploaded, users can expand "📊 Extraction Details & Traceability" to see:

#### Field Confidence Breakdown
- **Vendor Name**: Confidence level (High/Medium/Low)
- **Total Cost**: Currency and uncertainty indicators
- **Timeline**: Source document type indicator
- **Scope Coverage**: Number of items extracted

#### Processing Trace
- **Source Document Type**: PDF, DOCX, PPTX, XLSX, PNG, JPG, TXT
- **Extraction Status**: Pending, In Progress, Normalized, Failed
- **Scope Coverage**: Count of extracted scope items
- **Confidence Score**: Overall confidence metric

#### Field Extraction Breakdown Table
Shows each extracted field with:
- Field name
- Extracted value
- Confidence level (High/Medium/Low)

#### Scope Items
Complete list of all extracted scope items with enumeration

#### Compliance Terms
All detected compliance terms highlighted with checkmarks

### 1.2 Data Source Mapping
Every piece of extracted data includes:
- Source file type
- Extraction status
- Date/time of extraction (via audit trail)
- Processing confidence

## 2. Scoring Explainability

### 2.1 Score Components Breakdown
**Location:** Results & Scoring Tab → Scoring Breakdown & Methodology

For each vendor, displays:

#### Individual Score Metrics
- **Price Score** (0-10): "Lower is better"
- **Delivery Score** (0-10): "Higher is better" 
- **Compliance Score** (0-10): "Higher is better"
- **Weighted Score** (0-100): Overall ranking

#### Scoring Methodology
Explains the calculation formula:
```
Weighted Score = (Price Score × 40%) + (Delivery Score × 30%) + (Compliance Score × 30%)
```

### 2.2 Comparative Analysis
- **Vendor Comparison Table**: Shows all vendors' scores side-by-side
- **Score Distribution Chart**: Bar chart comparing price, delivery, and compliance scores across vendors
- **Rank Position**: Clear indication of where vendor ranks

### 2.3 Recommendation Justification
- **Top Vendor**: Highlighted with recommendation reasoning
- **Why Selected**: Explanation of selection criteria
- **Alternative Options**: Visibility into why other vendors ranked lower

## 3. Complete Audit Trail

### 3.1 Audit Trail Tab
**Location:** New 4th Tab - "📋 Audit Trail"

Provides complete record of all system activities:

#### Extraction Events Log
- Timestamp of each vendor upload
- Vendor name
- Event type (VENDOR_UPLOADED, EXTRACTION_COMPLETE, etc.)
- File size and extraction status
- Extraction confidence metrics

#### Scoring Events Log
- Timestamp of each scoring run
- RFQ ID
- Weights used (Price %, Delivery %, Compliance %)
- Scoring methodology version

#### Complete Timeline
Combined chronological view of all events with:
- Event type
- Timestamp
- Associated RFQ/Vendor
- Details and parameters

### 3.2 Event Types Tracked
1. **RFQ_CREATED**: When new RFQ is created
   - Project name
   - Budget
   - Timeline
   
2. **VENDOR_UPLOADED**: When vendor response uploaded
   - File name
   - File size
   - Extraction status
   
3. **EXTRACTION_COMPLETE**: When extraction finishes
   - Fields extracted
   - Confidence scores
   - Missing fields (if any)
   
4. **SCORING_COMPLETE**: When scoring runs
   - Weights used
   - Vendors scored
   - Timestamp

## 4. Data Lineage & Traceability

### 4.1 Field-Level Traceability
Each extracted field is traceable to:
1. **Source**: Original document (PDF, DOCX, etc.)
2. **Location**: Section of document if available
3. **Confidence**: Extraction confidence level
4. **Status**: Whether value was normalized or inferred
5. **Timestamp**: When extraction occurred

### 4.2 Score Calculation Traceability
Each score is traceable to:
1. **Vendor Data**: Which fields were used for scoring
2. **Weights**: Exact weights applied
3. **Formula**: Mathematical calculation shown
4. **Timestamp**: When scoring occurred
5. **Methodology**: Version of scoring algorithm used

## 5. User-Facing Transparency Features

### 5.1 Status Indicators
- ✅ **Success**: Operation completed successfully
- ⚠️ **Warning**: Attention needed, possible data quality issue
- ❌ **Error**: Operation failed
- ⏳ **In Progress**: Operation running
- 📋 **Info**: Additional information

### 5.2 Confidence Levels
- **High**: Data extracted with high confidence (95%+)
- **Medium**: Data extracted with moderate confidence (70-95%)
- **Low**: Data extracted with low confidence (<70%) or inferred

### 5.3 Visual Hierarchy
- **Expandable Sections**: Details hidden by default, expandable on demand
- **Metrics Cards**: Key metrics prominently displayed
- **Tables**: Comprehensive data in structured format
- **Charts**: Visual comparison of scores

## 6. User Interaction Flow

### Typical User Journey with Explainability

1. **Create RFQ** (Tab 1)
   - User creates new RFQ
   - Event logged with timestamp

2. **Upload Vendors** (Tab 2)
   - User uploads vendor responses
   - Automatic extraction occurs
   - User can expand "📊 Extraction Details" to see:
     - What was extracted
     - Confidence levels
     - Source document type
     - Scope items
     - Compliance terms

3. **Configure Scoring** (Tab 3)
   - User adjusts scoring weights
   - Weights validated
   - User clicks "▶ Run Scoring"

4. **Review Results** (Tab 3)
   - Vendor rankings displayed
   - User can expand "🎯 Scoring Breakdown"
   - Shows:
     - Score components
     - Calculation methodology
     - Comparative analysis
     - Recommendation justification

5. **Verify Audit Trail** (Tab 4)
   - User can review all events
   - See complete timeline
   - Understand decision history

## 7. Benefits of Explainability Features

### For Decision Makers
- Understand why vendors were ranked this way
- Trust the recommendations
- Make informed final decisions
- Audit compliance trail

### For Process Transparency
- Every step documented
- Reproducible results
- Version control of methodology
- Timestamp for all operations

### For Data Quality
- Confidence scores indicate data reliability
- Missing fields are flagged
- Inferred values are marked
- Source traceability

### For Compliance
- Complete audit trail
- Versioned scoring methodology
- Timestamped decisions
- Source documentation

## 8. Implementation Details

### Session State Management
- `extraction_logs`: Logs of all extraction events
- `scoring_logs`: Logs of all scoring events
- Persists within session
- Can be exported for external audit

### Logging Functions
- `log_extraction_event()`: Records extraction operations
- `log_scoring_event()`: Records scoring operations

### Display Functions
- `show_extraction_explainability()`: Shows extraction details
- `show_scoring_explainability()`: Shows scoring breakdown

## 9. Future Enhancements

Potential additions for enhanced traceability:
- Export audit trail to PDF/CSV
- Historical comparison (score changes over time)
- What-if analysis (simulate different weights)
- Model versioning and A/B testing
- User action log (who changed what, when)
-Machine learning explanation (LIME/SHAP for AI scores)

## 10. Summary

The enhanced frontend ensures:
- ✅ Every extraction is transparent and confident
- ✅ Every score is justified and explained
- ✅ Every decision can be audited
- ✅ Every insight is traceable to source
- ✅ Complete decision history preserved
- ✅ User trust in AI-assisted recommendations
