# RFQ AI System - Video Transcript (5 Minutes)

**[00:00-00:30] INTRODUCTION**

"Welcome to the RFQ AI Vendor Evaluation System – an intelligent platform that automates vendor assessment and scoring while maintaining complete transparency. Today, I'll show you how it transforms vendor quotations from multiple formats into standardized, scored recommendations with full traceability at every step."

**[00:30-01:15] SYSTEM FLOW OVERVIEW**

"The system works in four key phases. First, you create an RFQ – specifying your project, budget, timeline, and requirements. Second, vendors submit their quotations in any format – PDF, Word, PowerPoint, Excel, even images. Third, our AI extracts and normalizes vendor data across currencies and formats. Finally, we score vendors across price, delivery, and compliance criteria, and provide ranked recommendations. Throughout the entire process, every decision is explainable and traceable."

**[01:15-01:45] KEY DECISION #1: MULTI-FORMAT SUPPORT**

"Key decision one: We designed the system to accept vendor responses in ANY format. Most RFQ systems require standardized PDF submissions, which creates friction with vendors. Our system uses advanced extraction to handle PDFs, Word documents, PowerPoint presentations, Excel spreadsheets, and even photos or images that vendors might send. This dramatically increases vendor participation and reduces back-and-forth requests for formatted resubmissions."

"As you can see here, we have extraction functions for every major document type – extract_pdf, extract_docx, extract_pptx, extract_excel, and even OCR capability for scanned documents."

**[01:45-02:30] KEY DECISION #2: EXPLAINABILITY & TRACEABILITY**

"Key decision two: Complete transparency. Traditional vendor scoring is a black box – vendors get a score with no explanation, and procurement teams can't justify their decisions to stakeholders. We implemented full explainability at every step."

"When you upload a vendor response, you immediately see extraction confidence – which fields were extracted reliably, which were inferred by AI, and what the source document was. The system shows you exactly what was extracted: vendor name, cost in original currency normalized to USD, timeline, and any scope items or compliance terms detected."

"When scoring happens, you see exactly how each component score was calculated and how weights were applied. So when someone asks 'why did we pick this vendor?', you have the complete answer right there."

**[02:30-03:15] KEY DECISION #3: AUDIT TRAIL**

"Key decision three: Audit trail with complete event history. Procurement decisions need to be defensible. What if a stakeholder asks six months later 'why did we choose vendor X?'"

"Our audit trail captures every event – when the RFQ was created, when each vendor submitted, when extraction ran, when scores were calculated. Every operation is timestamped and searchable. This gives you complete defensibility – you can answer 'when did we score this RFQ?' instantly. If you need to explain a decision to an auditor or executive, you have the complete chain of events with timestamps."

**[03:15-04:15] LIVE DEMO: COMPLETE WORKFLOW**

"Now let me walk through a complete example. I'm going to create an RFQ, upload vendor quotations in different formats, run scoring, and show how the system handles everything automatically while maintaining full transparency."

"First, I'll create an RFQ for cloud infrastructure with a $500K budget and specific requirements around uptime and support. The system generates an ID for tracking – this ID ties everything together."

"Now I'm uploading the first vendor quotation – a PDF. The system automatically extracts: vendor name TechCorp Ltd, cost of $450,000 USD, timeline of 8 weeks, and identified that they have ISO 9001 and SOC 2 certifications. All fields show confidence levels – high confidence means we're sure about the extraction."

"Here's a Word document from another vendor – CloudFirst Solutions. Same extraction happens automatically, even though the format is completely different. The system normalizes both to the same structure so they're comparable."

"Now I run the scoring algorithm with the default weights – 40% on price competitiveness, 30% on delivery speed, 30% on compliance and capabilities. The system scores all vendors against these criteria."

"TechCorp comes in first with 82.3 out of 100. But here's where explainability matters – let me click on their result to see exactly why they won."

"You can see the breakdown: Price score 8.5 out of 10, delivery score 7.2 out of 10, compliance score 9.0 out of 10. The methodology is transparent – I can see the weighted calculation: 40% of 8.5 is 3.4, 30% of 7.2 is 2.2, 30% of 9.0 is 2.7, totaling 8.3."

"TechCorp wins because of strong compliance at 9 out of 10 despite slightly lower delivery speed compared to CloudFirst. You can see exactly how the weighted calculation works. This is defensible – you can show stakeholders the math."

"And here's the audit trail – every event timestamped. This is the complete history. Six months from now, when someone asks 'why did we pick TechCorp?', you can pull up this trail and the scoring details. You have complete defensibility."

**[04:15-04:45] KEY FEATURES SUMMARY**

"Let me highlight the key features that make this system powerful:"

"One – Multi-format extraction. We handle PDFs, Word docs, PowerPoint, Excel, images, even text files. Your vendors can submit however they want."

"Two – AI-powered normalization. We normalize currencies automatically. If a vendor quotes in EUR or GBP, it's converted to USD using current rates. Different ways of expressing timeline? We normalize that too."

"Three – Explainable AI scoring. Every decision is transparent. You see component scores, weights, calculations. No black box."

"Four – Complete traceability. Timestamped audit trail. Every event is recorded. Defensible decisions."

"Five – User-friendly interface. Four tabs, clear workflow. No complex setup required."

"Six – Live scores. Need to adjust weights? Change compliance emphasis from 30% to 40%? Recalculate instantly. See how rankings change."

**[04:45-05:00] FUTURE IMPROVEMENTS**

"If we continued development, we'd add:"

"Real-time collaboration – Multiple procurement teams could work on the same RFQ simultaneously with real-time updates."

"Advanced filtering – Users could filter vendors by specific criteria. 'Show me vendors under $400K with faster than 10-week delivery.'"

"Scenario analysis – 'What if we weight compliance at 50% instead of 30?' See alternative rankings instantly."

"Integration with vendor databases – Auto-populate known vendors, import from vendor management systems."

"ML-powered scoring – Over time, learn from past decisions. Which vendor selections led to successful projects? Update scoring weights accordingly."

"Mobile app – On-the-go access to RFQ status and scores."

**[05:00] CLOSING**

"The RFQ AI System transforms vendor evaluation from an opaque, manual process into a transparent, AI-enhanced, fully auditable workflow. You get faster decisions, better transparency, and complete defensibility. Thank you for watching."

---

## TRANSCRIPT METADATA

- **Total Duration:** 5:00 (300 seconds)
- **Words:** ~2,100
- **Reading Pace:** ~420 words/minute (normal conversational pace)
- **Key Takeaways:**
  1. System accepts vendor responses in any format
  2. Every decision is explainable and traceable
  3. Audit trail provides complete defensibility
  4. Scores are calculated transparently with visible weights
  5. Procurement can reconfigure scoring instantly
  
- **Call-to-Action:** "The RFQ AI System transforms vendor evaluation from an opaque, manual process into a transparent, AI-enhanced, fully auditable workflow."

---

## SPEAKER NOTES

- Speak clearly but conversationally – this is a tech demo, not a formal presentation
- Pause briefly after each key decision to let information sink in
- During live demo, speak the steps aloud as you perform them ("Now I'll click Create RFQ...")
- When showing data tables, point to specific values to guide viewer attention
- Emphasize the transparency and defensibility themes – this is what makes the system unique
- If screen is hard to read in video, consider zooming in on key sections
- Consider adding on-screen text labels/arrows during editing to highlight important elements
