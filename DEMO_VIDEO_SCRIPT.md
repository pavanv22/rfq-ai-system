# RFQ AI System - Demo Video Script (5 Minutes)

## Overview
This script guides a live demonstration of the RFQ AI Vendor Evaluation System, showcasing the complete workflow from RFQ creation through vendor scoring with full explainability and traceability.

---

## SCENE 1: Introduction (0:00-0:30)

**NARRATION:**
"Welcome to the RFQ AI Vendor Evaluation System – an intelligent platform that automates vendor assessment and scoring while maintaining complete transparency. Today, I'll show you how it transforms vendor quotations from multiple formats into standardized, scored recommendations with full traceability at every step."

**VISUAL:**
- Show system title screen: "RFQ AI Vendor Evaluation System"
- Display the 4 main tabs: RFQ Submission, Vendor Quotations, Results & Scoring, Audit Trail
- Brief animation showing data flow: Documents → Extraction → Scoring → Recommendations

---

## SCENE 2: System Flow Overview (0:30-1:15)

**NARRATION:**
"The system works in four key phases. First, you create an RFQ – specifying your project, budget, timeline, and requirements. Second, vendors submit their quotations in any format – PDF, Word, PowerPoint, Excel, even images. Third, our AI extracts and normalizes vendor data across currencies and formats. Finally, we score vendors across price, delivery, and compliance criteria, and provide ranked recommendations. Throughout the entire process, every decision is explainable and traceable."

**VISUAL - Show each phase:**
1. **Phase 1 - RFQ Setup:** 
   - Navigate to Tab 1: "RFQ Submission"
   - Show creating new RFQ form
   - Fill in: Project name, Budget, Timeline, Scope
   - Click "Create RFQ"

2. **Phase 2 - Vendor Upload:**
   - Navigate to Tab 2: "Vendor Quotations"
   - Show file upload interface
   - Display supported formats: PDF, DOCX, PPTX, XLSX, PNG, JPG, TXT

3. **Phase 3 - Extraction:**
   - Show extraction in progress
   - Highlight extracted fields: Vendor Name, Cost, Timeline, Scope

4. **Phase 4 - Scoring & Ranking:**
   - Navigate to Tab 3: "Results & Scoring"
   - Show scoring methodology
   - Display rankings and recommendations

---

## SCENE 3: Key Design Decision #1 - Multi-Format Support (1:15-1:45)

**NARRATION:**
"Key decision one: We designed the system to accept vendor responses in ANY format. Most RFQ systems require standardized PDF submissions, which creates friction with vendors. Our system uses advanced extraction to handle PDFs, Word documents, PowerPoint presentations, Excel spreadsheets, and even photos or images that vendors might send. This dramatically increases vendor participation and reduces back-and-forth requests for formatted resubmissions."

**VISUAL:**
- Show the file uploader with multiple file types displayed
- Demonstrate uploading a PDF
- Show successful extraction with status "normalized"
- Display the extracted data: vendor name, cost, timeline, scope items

**CODE HIGHLIGHT:**
- Show backend extraction functions: extract_pdf(), extract_docx(), extract_pptx(), extract_excel()
- Mention OCR capability for scanned documents

---

## SCENE 4: Key Design Decision #2 - Explainability & Traceability (1:45-2:30)

**NARRATION:**
"Key decision two: Complete transparency. Traditional vendor scoring is a black box – vendors get a score with no explanation, and procurement teams can't justify their decisions to stakeholders. We implemented full explainability at every step. When you upload a vendor response, you immediately see extraction confidence, which fields were extracted reliably, which were inferred by AI, and what the source document was. When scoring happens, you see exactly how each component score was calculated and how weights were applied."

**VISUAL:**
- Click on a vendor in Tab 2
- Show extraction explainability details: "📊 Extraction Details & Traceability"
- Display fields:
  - Vendor Name with confidence level
  - Cost in original currency and normalized USD
  - Timeline
  - Source document type (PDF, DOCX, etc.)
  - Extraction status (normalized, pending, incomplete)
  - Scope coverage (number of items)
  - Confidence indicators

- Show the "Field Extraction Breakdown" table:
  - Field name | Value | Confidence level

- Display detected compliance terms and scope items

**Navigate to Tab 3 - Results & Scoring:**
- Show scoring configuration (40% price, 30% delivery, 30% compliance)
- Click recommended vendor (top ranked)
- Expand "🎯 Scoring Breakdown & Methodology"
- Show individual component scores (Price, Delivery, Compliance)
- Display methodology explanation
- Show comparative analysis table (all vendors with their scores)

---

## SCENE 5: Key Design Decision #3 - Audit Trail (2:30-3:15)

**NARRATION:**
"Key decision three: Audit trail with complete event history. Procurement decisions need to be defensible. What if a stakeholder asks six months later 'why did we choose vendor X?' Our audit trail captures every event – when the RFQ was created, when each vendor submitted, when extraction ran, when scores were calculated, with timestamps. You can trace any decision back to its source."

**VISUAL:**
- Navigate to Tab 4: "📋 Audit Trail & Complete Traceability"
- Show two sections:
  - **Extraction Events:** Table showing
    - Timestamp
    - Vendor name
    - Event type (VENDOR_UPLOADED)
    - Source file
    - Extraction status
  
  - **Scoring Events:** Table showing
    - Timestamp
    - RFQ ID
    - Event type (SCORING_COMPLETE)
    - Details (weights used)

- Show "All Events Timeline" section
- Display chronological event list sorted by timestamp (newest first)
- Demonstrate filtering/searching capability if available

**NARRATION:**
"Every operation is timestamped and searchable. This gives you complete defensibility – you can answer 'when did we score this RFQ?' instantly."

---

## SCENE 6: Live Demo - Complete Workflow (3:15-4:15)

**NARRATION:**
"Let me walk through a complete workflow. First, I'll create a sample RFQ, upload several vendor quotations in different formats, run the scoring, and show you how the system automatically handles everything while maintaining full transparency."

### Step 1: Create RFQ (Tab 1)
**ACTION:**
- Go to "🗂️ RFQ Submission" tab
- Click "Create New RFQ"
- Fill form:
  - Project Name: "Cloud Infrastructure Migration"
  - Budget: $500,000
  - Timeline: 12 weeks
  - Type: RFQ
  - Scope: "Full cloud migration with 99.9% uptime SLA, 24/7 support, disaster recovery"
- Click "Create RFQ"
- Result: "✅ RFQ Created! ID: [hash]"

**NARRATION:**
"First, I've created an RFQ for cloud infrastructure with a $500K budget and specific requirements around uptime and support. The system generates an ID for tracking."

### Step 2: Upload Vendors (Tab 2)
**ACTION:**
- Go to "👥 Vendor Quotations" tab
- Select the created RFQ
- Upload vendor document #1 (PDF)
- System displays: "✅ TechCorp Ltd processed!"
- Show extraction details:
  - Vendor Name: TechCorp Ltd (High Confidence)
  - Cost: $450,000 USD
  - Timeline: 8 weeks
  - Status: Normalized
  - Scope Coverage: 5 items
  - Compliance: ISO 9001, SOC 2 Certified

**NARRATION:**
"I upload the first vendor quotation – a PDF. The system automatically extracts: vendor name, cost, timeline, and identified that they have ISO 9001 and SOC 2 certifications. All fields show confidence levels."

- Upload vendor document #2 (Word document)
- Show extraction for CloudFirst Solutions
- Display different format but same structured output

**NARRATION:**
"Here's a Word document from another vendor. Same extraction happens automatically, even though the format is completely different. The system normalizes both to the same structure."

- Show vendor comparison table:
  - Vendor | Cost | Timeline | Status | Source

### Step 3: Run Scoring (Tab 3)
**ACTION:**
- Go to "🏆 Results & Scoring" tab
- Check scoring weights (40% price, 30% delivery, 30% compliance)
- Click "▶ Run Scoring Analysis"
- System processes: "✅ Scoring completed!"

**NARRATION:**
"Now I run the scoring algorithm with the default weights – 40% on price competitiveness, 30% on delivery speed, 30% on compliance and capabilities. The system scores all vendors against these criteria."

### Step 4: View Results
**ACTION:**
- Show rankings table:
  - Rank | Vendor | Price 💰 | Delivery 📅 | Compliance ✅ | Score 🎯
  - #1 | TechCorp Ltd | 8.5 | 7.2 | 9.0 | 82.3
  - #2 | CloudFirst Solutions | 7.5 | 8.1 | 8.0 | 78.9

**NARRATION:**
"TechCorp comes in first with 82.3/100. But here's where explainability matters – let me click on their result to see exactly why they won..."

- Click on TechCorp recommendation
- Expand "🎯 Scoring Breakdown & Methodology"
- Show metrics:
  - Price Score: 8.5/10
  - Delivery Score: 7.2/10
  - Compliance Score: 9.0/10
  - Overall: 82.3/100

- Show methodology:
  - "40% Price (40% × 8.5 = 3.4)"
  - "30% Delivery (30% × 7.2 = 2.2)"
  - "30% Compliance (30% × 9.0 = 2.7)"
  - "Total: 8.3/100"

- Show recommendation justification:
  - "✅ This vendor is recommended because:"
  - "Highest overall weighted score"
  - "Balanced performance across all criteria"
  - "Meets compliance requirements"

**NARRATION:**
"TechCorp wins because of strong compliance (9.0) despite slightly lower delivery speed compared to CloudFirst. You can see exactly how the weighted calculation works. This is defensible – you can show stakeholders the math."

### Step 5: View Audit Trail (Tab 4)
**ACTION:**
- Go to "📋 Audit Trail" tab
- Show complete timeline:
  - 2026-04-11 14:30:00 | RFQ_CREATED | Cloud Infrastructure Migration RFQ created
  - 2026-04-11 14:35:00 | VENDOR_UPLOADED | TechCorp Ltd submitted (PDF)
  - 2026-04-11 14:40:00 | EXTRACTION_COMPLETE | TechCorp extraction - High confidence
  - 2026-04-11 14:42:00 | VENDOR_UPLOADED | CloudFirst Solutions submitted (DOCX)
  - 2026-04-11 14:47:00 | EXTRACTION_COMPLETE | CloudFirst extraction - High confidence
  - 2026-04-11 14:50:00 | SCORING_COMPLETE | Scoring run complete with weights: 40/30/30
  - 2026-04-11 14:51:00 | RECOMMENDATION_GENERATED | TechCorp Ltd ranked #1

**NARRATION:**
"This is the complete audit trail – every event timestamped. Six months from now, when someone asks 'why did we pick TechCorp?', you can pull up this trail and the scoring details. You have complete defensibility."

---

## SCENE 7: Key Features Summary (4:15-4:45)

**NARRATION:**
"Let me highlight the key features that make this system powerful:

One – **Multi-format extraction.** We handle PDFs, Word docs, PowerPoint, Excel, images, even text files. Your vendors can submit however they want.

Two – **AI-powered normalization.** We normalize currencies automatically. If a vendor quotes in EUR or GBP, it's converted to USD using current rates. Different ways of expressing timeline? We normalize that too.

Three – **Explainable AI scoring.** Every decision is transparent. You see component scores, weights, calculations. No black box.

Four – **Complete traceability.** Timestamped audit trail. Every event is recorded. Defensible decisions.

Five – **User-friendly interface.** Four tabs, clear workflow. No complex setup required.

Six – **Live scores.** Need to adjust weights? Change compliance emphasis from 30% to 40%? Recalculate instantly. See how rankings change."

**VISUAL:**
- Quick screen capture of each feature being highlighted

---

## SCENE 8: What We Would Improve (4:45-5:00)

**NARRATION:**
"If we continued development, we'd add:

**Real-time collaboration** – Multiple procurement teams could work on the same RFQ simultaneously, with real-time updates.

**Advanced filtering** – Users could filter vendors by specific criteria. 'Show me vendors under $400K with faster than 10-week delivery.'

**Scenario analysis** – 'What if we weight compliance at 50% instead of 30?' See alternative rankings instantly.

**Integration with vendor databases** – Auto-populate known vendors, import from vendor management systems.

**ML-powered scoring** – Over time, learn from past decisions. Which vendor selections led to successful projects? Update scoring weights accordingly.

**Mobile app** – On-the-go access to RFQ status and scores."

**VISUAL:**
- Show roadmap slide with these features marked as "Future Release"

---

## CLOSING (5:00)

**NARRATION:**
"The RFQ AI System transforms vendor evaluation from an opaque, manual process into a transparent, AI-enhanced, fully auditable workflow. You get faster decisions, better transparency, and complete defensibility. Thank you for watching."

**VISUAL:**
- Logo slide
- Contact/Links slide
- "Questions?" prompt

---

## TECHNICAL NOTES FOR PRESENTER

- **Timing:** Each main section is roughly 1 minute. Adjust pacing based on audience questions.
- **Data to prepare:** Create 2-3 sample vendor quotations in different formats (PDF, DOCX) with realistic data
- **System state:** Ensure backend is running on port 8001, Streamlit frontend is running
- **Network:** Perform demo with stable internet/local network connection
- **Backup:** Record key steps in advance in case of live system issues
- **Engagement:** Pause at key decision points for audience questions
