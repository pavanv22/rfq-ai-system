================================================================================
                    TEST VENDOR FILES - USAGE GUIDE
================================================================================

The following test files have been created in:
c:\Users\pavan\apps-pavan\rfq-ai-system\test_vendors\

Each file is designed to test different extraction and processing scenarios.

================================================================================
                         FILE INVENTORY & PURPOSE
================================================================================

1. vendor_01_techcore.txt (5 KB)
   Status: Ready to test
   Format: TXT (or save as PDF/DOCX)
   Complexity: SIMPLE
   Features:
   ✓ Cleanly formatted vendor quote
   ✓ Single currency (USD)
   ✓ Clear pricing breakdown
   ✓ Complete information
   ✓ Standard timeline in days
   
   Testing Purpose: Baseline test - should extract cleanly
   Expected Fields: Vendor name, cost, timeline, scope
   

2. vendor_02_cloudfirst.txt (8 KB)
   Status: Ready to test
   Format: TXT (or save as PDF/DOCX)
   Complexity: MEDIUM
   Features:
   ✓ European vendor format (slightly different style)
   ✓ Multiple currencies (EUR)
   ✓ Complex invoice structure
   ✓ References in German and English
   ✓ Price options (A/B comparison)
   
   Testing Purpose: Multi-language and currency handling
   Expected Fields: Vendor name (EUR), costs in euros, conversion rates
   Challenge: Different field naming conventions


3. vendor_03_india_incomplete.txt (6 KB)
   Status: Ready to test
   Format: TXT (or save as DOCX)
   Complexity: CHALLENGING
   Features:
   ✓ Indian vendor (INR pricing)
   ✓ INCOMPLETE pricing (missing fields marked)
   ✓ Confusing cost structure
   ✓ Some items marked "TBD" or "TO BE CONFIRMED"
   ✓ Approximate cost ranges instead of exact prices
   ✓ Mixed numeric formats (₹ and USD references)
   
   Testing Purpose: Missing field detection & AI inference
   Expected Challenge: System must identify missing costs
   Expected Action: Normalizer should flag incomplete fields
   Opportunity: Test AI inference for missing timeline/costs


4. vendor_04_global_mixed_currency.txt (25 KB)
   Status: Ready to test
   Format: TXT (or save as DOCX - simulates Word)
   Complexity: ADVANCED
   Features:
   ✓ Multi-page document (40+ sections)
   ✓ THREE different currencies (USD, EUR, GBP)
   ✓ Confusing naming conventions:
     - "Project Fee" vs "Total Implementation Cost"
     - "Grand Total for Execution"
     - "Complete Solution Investment"
   ✓ Pricing spread across multiple sections
   ✓ Complex subtotals and invoice structures
   ✓ Same information named differently in different places
   ✓ Long-form narrative with embedded pricing
   
   Testing Purpose: Complex document parsing, naming variation handling
   Expected Challenge: Extract correct total from confusing layout
   Challenge: Must aggregate pricing from 5+ different sections
   Currency Handling: Convert EUR/GBP to USD correctly


5. vendor_05_budget_excel.csv (4 KB)
   Status: Ready to test (CSV format - simulates Excel)
   Format: CSV (open/save as XLSX in Excel)
   Complexity: ADVANCED
   Features:
   ✓ Tabular data format
   ✓ Multiple vendor lines
   ✓ Split across invoice sections (A, B, C)
   ✓ Dual currency columns (USD and EUR)
   ✓ Complex calculations required
   ✓ Subtotals and grand totals in different places
   ✓ Footnotes and notes in text
   
   Testing Purpose: Table extraction and tabular data parsing
   Expected Action: Extract line items and calculate totals
   Challenge: Multiple invoice sections need aggregation


6. vendor_06_comprehensive_long.txt (35 KB)
   Status: Ready to test (Extremely long document)
   Format: TXT (or save as DOCX)
   Complexity: EXTREME
   Features:
   ✓ 45+ page equivalent document (full proposal with all sections)
   ✓ Multiple pricing sections (3 detailed components)
   ✓ Confusing layout with repeated pricing info
   ✓ Embedded tables and data structures
   ✓ Long narrative sections mixed with pricing
   ✓ Optional add-on pricing
   ✓ Alternative payment terms with different totals
   ✓ Executive summary + detailed breakdown
   
   Testing Purpose: Handle very long documents without information loss
   Expected Challenge: Extract pricing from 45+ pages of content
   Purpose: Verify system handles document length without timeout
   Data Accuracy: Ensure no information loss in long crawl


7. vendor_07_with_images_ppt.txt (12 KB)
   Status: Ready to test (Simulates PPT with image content)
   Format: TXT (simulates extracted PPT text)
   Complexity: ADVANCED
   Features:
   ✓ Image reference descriptions (13 image placeholders)
   ✓ Contains information only in image descriptions
   ✓ Diagrams and visual data referenced but not in text
   ✓ Charts described as text:
     - Pie chart with percentages
     - Gantt chart with timeline
     - Network diagram with topology
     - Security layers visualization
   ✓ Pricing in visual formats described in text
   
   Testing Purpose: Handle image-embedded content and visual data
   Expected Challenge: Extract data from image descriptions
   Data Source: All data available only through image metadata


================================================================================
                        TESTING COMPLEXITY MATRIX
================================================================================

File              Format    Currencies    Complexity  Extraction  Notes
────────────────────────────────────────────────────────────────────────
vendor_01        TXT       1 (USD)       ★☆☆☆☆      EASY        Baseline
vendor_02        TXT       1 (EUR)       ★★☆☆☆      MEDIUM      Language variation
vendor_03        TXT       2 (INR+USD)   ★★☆☆☆      MEDIUM      Missing fields
vendor_04        TXT       3 (USD/EUR/GBP) ★★★★☆    HARD        Naming confusion
vendor_05        CSV       2 (USD/EUR)   ★★★★☆      HARD        Tabular data
vendor_06        TXT       1 (USD)       ★★★★★      HARDEST     Very long doc
vendor_07        TXT       1 (USD)       ★★★☆☆      MEDIUM      Image references


================================================================================
                        CONVERSION TO PROPER FORMATS
================================================================================

To test the system with multiple file formats (PDF, Word, Excel, PPT), you
have several options:

OPTION 1: MANUAL CONVERSION (Easiest)
─────────────────────────────────────
1. Open each text file in your default text editor
2. Save As with appropriate format:
   
   vendor_01_techcore.txt      → Save As vendor_01.docx (Word format)
   vendor_02_cloudfirst.txt    → Save As vendor_02.pdf  (PDF format)
   vendor_03_india_incomplete  → Save As vendor_03.docx
   vendor_04_global_mixed      → Save As vendor_04.pdf
   vendor_05_budget_excel.csv  → Open in Excel, Save As vendor_05.xlsx
   vendor_06_comprehensive     → Save As vendor_06.docx
   vendor_07_with_images_ppt   → Save As vendor_07.pptx (PowerPoint)


OPTION 2: AUTOMATED CONVERSION (Command-line)
──────────────────────────────────────────────
Install LibreOffice and use command-line conversion:

Convert CSV to XLSX:
  libreoffice --headless --convert-to xlsx vendor_05_budget_excel.csv

Convert TXT to PDF:
  libreoffice --headless --convert-to pdf vendor_01_techcore.txt

Convert TXT to DOCX:
  libreoffice --headless --convert-to docx vendor_02_cloudfirst.txt


OPTION 3: PYTHON SCRIPT (Programmatic)
───────────────────────────────────────
Use Python with libraries like python-pptx, python-docx, openpyxl:

```python
# Create DOCX from TXT
from docx import Document
doc = Document()
with open('vendor_01_techcore.txt', 'r') as f:
    doc.add_paragraph(f.read())
doc.save('vendor_01.docx')

# Create XLSX from CSV
import openpyxl, csv
wb = openpyxl.Workbook()
ws = wb.active
with open('vendor_05_budget_excel.csv', 'r') as f:
    for row in csv.reader(f):
        ws.append(row)
wb.save('vendor_05.xlsx')
```


OPTION 4: ONLINE CONVERSION TOOLS
──────────────────────────────────
- CloudConvert: https://cloudconvert.com
- Zamzar: https://www.zamzar.com
- LuckyPDF: https://www.luckyorange.com/pdf-tools
- Convertio: https://convertio.co


================================================================================
                        RECOMMENDED TEST SEQUENCE
================================================================================

PHASE 1: BASIC EXTRACTION (Test single vendor at a time)
─────────────────────────────────────────────────────────

1. Start with vendor_01 (Simple USD pricing)
   Format: TXT or DOCX
   Expected: All fields extracted correctly
   Success Criteria: Vendor name, cost $45,000, timeline 3 weeks

2. Test vendor_02 (Different format, EUR pricing)
   Format: PDF or DOCX
   Expected: Handle different layout, convert EUR to USD
   Success Criteria: Cost normalized to USD, ~$45,500 equivalent

3. Test vendor_03 (Incomplete data)
   Format: TXT or DOCX
   Expected: Flag missing fields, attempt AI inference
   Success Criteria: Detect [COST NOT PROVIDED] items


PHASE 2: ADVANCED EXTRACTION (Test complex scenarios)
────────────────────────────────────────────────────

4. Test vendor_04 (Mixed currencies, confusing naming)
   Format: DOCX or PDF
   Expected: Aggregate pricing from multiple sections, consolidate currencies
   Success Criteria: Identify correct total from confusing layout
   Challenge: Extract true total from "Total Implementation Cost" vs others

5. Test vendor_05 (Tabular data)
   Format: XLSX (Excel)
   Expected: Extract table data, sum line items correctly
   Success Criteria: Calculate subtotals A+B+C correctly

6. Test vendor_06 (Very long document)
   Format: PDF or DOCX
   Expected: Process entire 45+ page equivalent without failure
   Success Criteria: Extract pricing accurately despite length
   Performance: Should complete within reasonable time


PHASE 3: EDGE CASES (Test system resilience)
──────────────────────────────────────────────

7. Test vendor_07 (Image-embedded data)
   Format: TXT (simulating PPT)
   Expected: Handle image descriptions, extract visual data
   Success Criteria: Identify pricing in image description text


================================================================================
                        EXPECTED EXTRACTION RESULTS
================================================================================

vendor_01_techcore: USD $45,000, 3 weeks, TechCore Solutions
vendor_02_cloudfirst: EUR €42,000 (~$45,540 USD), 4 weeks, CloudFirst Systems
vendor_03_india_incomplete: ₹3.6-4.2M INR (~$43-50K USD), 17 days, SecureNet India
  [Missing: Some licensing costs marked TBD]
vendor_04_global_mixed: Multiple currencies! USD $65K + EUR €27.7K + £13.3K GBP
  = ~$111,751 USD (hardware alone) + services
  [Challenge: Confusing naming conventions throughout]
vendor_05_budget_excel: Sum of all invoices A+B+C = $248,210 USD (or €227,065)
  [Multi-invoice structure across rows]
vendor_06_comprehensive: Core = $1,461,800 USD total (includes contingency)
  [Alternative payment terms also present]
vendor_07_with_images_ppt: $155,000 USD (from text descriptions of image charts)
  [Additional image data would be visual only]


================================================================================
                        KEY EXTRACTION CHALLENGES
================================================================================

Challenge #1: CURRENCY MIXING
Location: vendor_04, vendor_05
Issue: Prices in USD, EUR, GBP, INR all in same document
Solution: System must normalize all to USD using rates provided


Challenge #2: NAMING VARIATIONS
Location: vendor_04
Issue: Same total price called:
  - "Total Implementation Cost"
  - "Grand Total for Execution"
  - "Complete Solution Investment"
  - Final invoice sum
Solution: Use multiple keywords, aggregate sections


Challenge #3: INCOMPLETE DATA
Location: vendor_03
Issue: Fields marked "TBD", "[COST NOT PROVIDED]", "TO BE CONFIRMED"
Solution: Detection and AI inference or flag as missing


Challenge #4: DOCUMENT LENGTH
Location: vendor_06
Issue: 45+ pages of content, pricing scattered throughout
Solution: Robust parsing, memory management, no timeout


Challenge #5: IMAGE DATA
Location: vendor_07
Issue: Important pricing data only in image/chart descriptions
Solution: Parse image metadata text for embedded data


Challenge #6: TABULAR DATA
Location: vendor_05
Issue: Multi-part invoices, columns in USD/EUR, subtotals scattered
Solution: Table recognition, numeric aggregation


Challenge #7: LONG-FORM NARRATIVE
Location: vendor_04, vendor_06
Issue: Pricing mixed with descriptive text across many pages
Solution: Section parsing, keyword extraction, context understanding

================================================================================
                        TESTING INSTRUCTIONS
================================================================================

For each file, in Streamlit Tab 2 (Vendor Quotations):

1. Select your RFQ
2. Click "Upload & Process" 
3. Choose one of the vendor files
4. System will:
   ✓ Extract text from file
   ✓ Parse for vendor name, cost, timeline
   ✓ Normalize currency to USD
   ✓ Detect missing fields
   ✓ Store in database
   ✓ Flag any extraction issues

4. Check the results:
   ✓ Vendor appears in Tab 2 "Uploaded Vendors" list
   ✓ Cost shows in USD
   ✓ Timeline extracted correctly
   ✓ Status shows extraction result ("completed" or "incomplete")

5. View extraction details:
   ✓ Check backend logs for any warnings
   ✓ Verify database contains expected data

================================================================================
                        SUCCESS METRICS
================================================================================

System should successfully:

✓ Extract all 7 vendor files without crashing
✓ Correctly identify vendor names (7/7)
✓ Extract costs (all values captured, even if approximate)
✓ Convert currencies to USD using provided rates
✓ Determine timelines (all 7 files have timeline info)
✓ Flag incomplete/missing data appropriately
✓ Handle files from 5 KB to 35 KB without performance issues
✓ Support text, CSV, and reference files
✓ Generate reasonable AI inferences for missing data

Ideal Results:
- 100% extraction success rate on all 7 files
- Currency normalization within 2% of actual rates
- Missing field detection accuracy >90%
- Processing time <30 seconds per file


================================================================================
                        NEXT STEPS
================================================================================

1. CREATE RFQ in Tab 1
   - Project: "IT Infrastructure Upgrade"
   - Budget: $500,000
   - Timeline: 8 weeks

2. UPLOAD ALL 7 VENDORS in Tab 2
   - Start with vendor_01 (easiest)
   - Progress to vendor_07 (most complex)
   - Monitor extraction results

3. RUN SCORING in Tab 3
   - Let system score all vendors
   - Review pricing normalization
   - Verify ranking is logical

4. VALIDATE RESULTS
   - Check vendor table shows correct costs in USD
   - Verify missing fields are flagged
   - Review scoring breakdown

5. TEST PERSISTENCE
   - Restart backend
   - Verify vendors still exist in database
   - Check no data loss occurred

================================================================================

Ready to test? Start with vendor_01_techcore.txt and work your way through!

Questions? Check the vendor file descriptions above for what each tests.

Good luck! 🚀

================================================================================
