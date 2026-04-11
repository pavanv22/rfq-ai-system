#!/usr/bin/env python3
"""Test improved extraction on CreativeEdge proposal"""

from app.agents.extraction_agent import fallback_extraction

# Sample text from the PDF (key sections)
pdf_text = """
COMMERCIAL PROPOSAL
CreativeEdge Communications Pvt. Ltd.
Response to: RFQ-MKT-KIDS-GL-2026-001
Global Launch – New Kids Health Drink
Prepared By: CreativeEdge Communications Pvt. Ltd.
Prepared For: Global Brand Marketing Team
Contact: Rajesh Mehta, Business Head | r.mehta@creativeedge.in
Date: April 10, 2026
Version: v2.1 – Final Commercial Submission
Validity: 90 days from date of submission

SECTION 9.2 Consolidated Project Fee Summary

The following table presents the complete consolidated commercial summary for all 8 workstreams. This is
the definitive pricing reference for evaluation purposes.

Section Description Agency Fee (INR)
A Strategy & Creative Development (Lots 1 & 2) 44,65,000
B TVC Production (Lot 3) 55,40,000
C Social & Digital Content (Lots 4, 5 & 6) 1,02,60,000
D Compliance & Program Management (Lots 7 & 8) 71,40,000

Total Agency Fees (A+B+C+D) 2,74,05,000
GST @ 18% 49,32,900
Estimated OOP / Pass-through (actuals basis) 20,00,000

TOTAL PROJECT FEE (incl. GST + OOP estimate) 3,43,37,900

Currency: All amounts above are quoted in Indian Rupees (INR). For international benchmarking, the
approximate USD equivalent at current exchange rate (1 USD = 83.5 INR) is USD 41,12,071 for the total
project fee.

SECTION 8. Timelines & Delivery Plan

Milestone Deliverable Timeline
Kick-off Stakeholder briefing, team onboarding Week 1 (May 5, 2026)
Strategy Submission Brand positioning + messaging architecture Week 3 (May 19, 2026)
Creative Territories 3 creative directions for review Week 6 (June 9, 2026)
TVC Concept Lock Approved TVC script + storyboard Week 8 (June 23, 2026)
Pre-Production Complete Casting, locations, crew confirmed Week 10 (July 7, 2026)
TVC Shoot Principal photography (2-3 days) Week 12 (July 20-22, 2026)
TVC Post-Production Edit, VFX, color, sound Week 15 (Aug 10, 2026)
Master TVC Delivery All formats + cutdowns delivered Week 17 (Aug 24, 2026)
Social Content Launch Month 1 content calendar live Week 14 (Aug 3, 2026)
Paid Media Activation All campaigns live Week 18 (Aug 31, 2026)
Compliance Certificates All market compliance sign-offs Week 16 (Aug 17, 2026)
Final Reporting Post-campaign performance report Week 28 (Oct 26, 2026)

SECTION 3. Understanding of Scope

Lot 1 Strategy & Creative Development - Full scope coverage
Lot 2 TVC Development - Full scope coverage
Lot 3 TVC Production - Full scope coverage
Lot 4 Social Organic Content - Full scope coverage
Lot 5 Social Paid Media Planning - Full scope coverage
Lot 6 Social Paid Media Buying & Optimization - Full scope coverage
Lot 7 Kids Advertising & Claims Compliance Review - Full scope coverage
Lot 8 Launch Program Management - Full scope coverage
"""

print("Testing improved extraction on CreativeEdge proposal...\n")

result = fallback_extraction(pdf_text)

print("EXTRACTION RESULT:")
print(f"  Vendor Name: {result.get('vendor_name')}")
print(f"  Total Cost: {result.get('total_cost')}")
print(f"  Currency: {result.get('currency')}")
print(f"  Timeline (weeks): {result.get('timeline_weeks')}")
print(f"  Scope Coverage: {result.get('scope_coverage')}")
print(f"\n✓ Expected: 3,43,37,900 INR")
print(f"✓ Expected: CreativeEdge Communications")
print(f"✓ Expected: Timeline around 28 weeks")
