import openai
import json
import re
openai.api_base = "http://localhost:11434/v1"
openai.api_key = "not-needed"

def clean_json(text):
    return text.replace("```json", "").replace("```", "").strip()  

def find_consolidated_summary(raw_text):
    """Find and parse consolidated summary section for financial data"""
    try:
        # Priority 1: Look for "Total Project Fee (incl. GST)" or similar total lines
        total_patterns = [
            r'TOTAL\s+(?:PROJECT\s+)?(?:FEE|COST).*?\(.*?GST.*?\)\s*\|?\s*([\d,\.]+)',
            r'TOTAL\s+(?:PROJECT\s+)?(?:FEE|COST).*?\(incl\.\s+GST\).*?\|?\s*([\d,\.]+)',
            r'Total.*?Project.*?Fee.*?\(incl\.\s+GST\).*?\|?\s*([\d,\.]+)',
            r'TOTAL\s+COST.*?\(incl\.\s+GST\).*?\|?\s*([\d,\.]+)',
            r'₹\s*([\d,]+)\s*$.*?Total\s+Cost.*?Project\s+Fee',  # Match with rupee symbol
        ]
        
        for pattern in total_patterns:
            match = re.search(pattern, raw_text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
            if match:
                amount = match.group(1)
                print(f"[EXTRACTION DEBUG] Found 'Total Project Fee' line: {amount}")
                return amount
        
        # Priority 2: Look for "TOTAL\s+.*?\d" patterns that are clearly totals
        total_match = re.search(r'\bTOTAL\b[^\n]*\|?\s*([\d,\.]+)\s*$', raw_text, re.MULTILINE | re.IGNORECASE)
        if total_match:
            print(f"[EXTRACTION DEBUG] Found TOTAL line: {total_match.group(1)}")
            return total_match.group(1)
        
        return None
    except Exception as e:
        print(f"[EXTRACTION DEBUG] Consolidated summary error: {e}")
        return None

def extract_vendor_name_from_header(raw_text):
    """Extract vendor/company name from document header - prioritizes explicit markers"""
    lines = raw_text.split('\n')
    
    # Strategy 1: Look for explicit "Prepared By:" or "Company:" lines
    for line in lines[:50]:
        line_clean = line.strip()
        if line_clean.lower().startswith("prepared by:"):
            # Extract company name after "Prepared By:"
            company = line_clean[len("prepared by:"):].strip()
            if company and len(company) > 3:
                # Extract just the company name part (before metadata)
                company = company.split("|")[0].split("(")[0].strip()
                if company and len(company) > 3:
                    return company
        elif line_clean.lower().startswith("company:") or line_clean.lower().startswith("company name:"):
            company = line_clean.split(":", 1)[1].strip()
            if company and len(company) > 3:
                return company
    
    # Strategy 2: Look for "PIXELCRAFT STUDIOS" or all-caps company names at the top
    for line in lines[:20]:
        line_clean = line.strip()
        if line_clean.isupper() and len(line_clean) > 5 and len(line_clean) < 80:
            # All caps indicates a company name/title
            if not any(skip in line_clean for skip in ["RFQ", "REQUEST", "RESPONSE", "PROPOSAL"]):
                return line_clean
    
    # Strategy 3: Look for company name patterns with Ltd, Pvt, Inc, etc. in first 30 lines
    for line in lines[:30]:
        line_clean = line.strip()
        if not line_clean or len(line_clean) < 5:
            continue
        # Skip common headers
        if any(skip in line_clean.lower() for skip in ["response to:", "rfq", "prepared ", "date:", "version:", "validity:", "submitted", "contact"]):
            continue
        # Look for company indicators (but avoid generic suffixes at the end of lines)
        if any(keyword in line_clean.lower() for keyword in ["pvt ltd", "pvt. ltd", "ltd"]):
            return line_clean
    
    # Strategy 4: Look for any capitalized phrase that seems like a company name
    for line in lines[:15]:
        line_clean = line.strip()
        if len(line_clean) > 10 and len(line_clean) < 100:
            # Check if it looks like a company name
            if line_clean[0].isupper() and not line_clean.isupper():
                # Avoid obvious non-company lines
                if not any(skip in line_clean.lower() for skip in ["document", "title", "chapter", "section"]):
                    return line_clean
    
    return "Unknown Vendor"

def fallback_extraction(raw_text):
    """Fallback regex-based extraction when AI fails - process ENTIRE document"""
    if not raw_text:
        return {
            "error": "No text extracted from document"
        }
    
    try:
        data = {
            "vendor_name": extract_vendor_name_from_header(raw_text),
            "total_cost": None,
            "currency": "USD",
            "timeline_weeks": 4,
            "scope_coverage": [],
            "key_terms": []
        }
        
        print(f"[EXTRACTION DEBUG] Vendor name: {data['vendor_name']}")
        print(f"[EXTRACTION DEBUG] Raw text length: {len(raw_text)} chars")
        
        # ===== COST EXTRACTION =====
        # Strategy: Look for TOTAL amounts first, then other large numbers
        # Priority: INR Total > INR large amounts > USD > EUR > GBP > Generic currency codes
        
        # 1a. Try INR with "TOTAL" prefix - this is the most reliable
        total_inr_match = re.search(
            r'\bTOTAL.*?[\r\n].*?(?:₹|INR)\s*([\d,\.]+)',
            raw_text,
            re.IGNORECASE | re.DOTALL | re.MULTILINE
        )
        if total_inr_match:
            try:
                cost_str = total_inr_match.group(1)
                cost_val = float(cost_str.replace(",", ""))
                if cost_val > 100:
                    data["total_cost"] = cost_val
                    data["currency"] = "INR"
                    print(f"[EXTRACTION DEBUG] Found TOTAL INR cost: {cost_str} → {cost_val}")
            except Exception as e:
                print(f"[EXTRACTION DEBUG] TOTAL INR parsing error: {e}")
        
        # 1b. Try looking for "Total Project Fee (incl. GST)" or similar patterns with rupee
        if not data["total_cost"]:
            project_fee_match = re.search(
                r'(?:Total\s+)?(?:Project\s+)?Fee.*?\(incl\.\s+GST\).*?[|\s]*(₹|INR)?\s*([\d,\.]+)',
                raw_text,
                re.IGNORECASE | re.MULTILINE
            )
            if project_fee_match:
                try:
                    cost_val = float(project_fee_match.group(2).replace(",", ""))
                    if cost_val > 100:
                        data["total_cost"] = cost_val
                        data["currency"] = "INR"
                        print(f"[EXTRACTION DEBUG] Found Project Fee (incl. GST) INR cost: {cost_val}")
                except Exception as e:
                    print(f"[EXTRACTION DEBUG] Project Fee parsing error: {e}")
        
        # 1c. Try INR amounts in general - but prefer larger ones (likely totals)
        inr_matches = re.finditer(r'(?:₹|INR)\s*([\d,\.]+)', raw_text, re.IGNORECASE | re.MULTILINE)
        inr_amounts = []
        for match in inr_matches:
            try:
                cost_str = match.group(1)
                cost_val = float(cost_str.replace(",", ""))
                if cost_val > 100:
                    inr_amounts.append(cost_val)
            except:
                pass
        
        if inr_amounts:
            # Use the largest INR amount (most likely to be the total)
            max_inr = max(inr_amounts)
            data["total_cost"] = max_inr
            data["currency"] = "INR"
            print(f"[EXTRACTION DEBUG] Found INR cost (largest of {len(inr_amounts)}): {max_inr}")
        
        # 2. If no INR found, look for consolidated summary amounts (large round numbers)
        if not data["total_cost"]:
            summary_amount = find_consolidated_summary(raw_text)
            if summary_amount:
                try:
                    cost_val = float(summary_amount.replace(",", "").replace(".", ""))
                    if cost_val > 50000:  # Large number, likely project cost
                        data["total_cost"] = cost_val
                        # Check if INR is mentioned in the document
                        if "inr" in raw_text.lower():
                            data["currency"] = "INR"
                        else:
                            data["currency"] = "USD"
                        print(f"[EXTRACTION DEBUG] Found summary cost: {cost_val}")
                except:
                    pass
        
        # 3. Try USD with TOTAL prefix first, then fall back to any USD
        if not data["total_cost"]:
            total_usd_match = re.search(
                r'\bTOTAL[^$\n]*?\$\s*([\d,]+(?:\.\d{2})?)',
                raw_text,
                re.IGNORECASE | re.MULTILINE
            )
            if total_usd_match:
                try:
                    cost_val = float(total_usd_match.group(1).replace(",", ""))
                    if cost_val > 1000:
                        data["total_cost"] = cost_val
                        data["currency"] = "USD"
                        print(f"[EXTRACTION DEBUG] Found TOTAL USD cost: {cost_val}")
                except:
                    pass
        
        # 3b. Try any USD amount
        if not data["total_cost"]:
            usd_amounts = []
            usd_matches = re.finditer(r'\$\s*([\d,]+(?:\.\d{2})?)', raw_text)
            for match in usd_matches:
                try:
                    cost_val = float(match.group(1).replace(",", ""))
                    if cost_val > 1000:  # Reasonable USD amount
                        usd_amounts.append(cost_val)
                except:
                    pass
            if usd_amounts:
                # Use largest USD amount if multiple found
                data["total_cost"] = max(usd_amounts)
                data["currency"] = "USD"
                print(f"[EXTRACTION DEBUG] Found USD cost (largest of {len(usd_amounts)}): {data['total_cost']}")
        
        # 4. Try EUR with TOTAL prefix first, then fall back to any EUR
        if not data["total_cost"]:
            total_eur_match = re.search(
                r'\bTOTAL[^€\n]*?€\s*([\d,]+(?:\.\d{2})?)',
                raw_text,
                re.IGNORECASE | re.MULTILINE
            )
            if total_eur_match:
                try:
                    cost_val = float(total_eur_match.group(1).replace(",", ""))
                    if cost_val > 1000:
                        data["total_cost"] = cost_val
                        data["currency"] = "EUR"
                        print(f"[EXTRACTION DEBUG] Found TOTAL EUR cost: {cost_val}")
                except:
                    pass
        
        # 4b. Try any EUR amount
        if not data["total_cost"]:
            eur_amounts = []
            eur_matches = re.finditer(r'€\s*([\d,]+(?:\.\d{2})?)', raw_text)
            for match in eur_matches:
                try:
                    cost_val = float(match.group(1).replace(",", ""))
                    if cost_val > 1000:
                        eur_amounts.append(cost_val)
                except:
                    pass
            if eur_amounts:
                # Use largest EUR amount if multiple found
                data["total_cost"] = max(eur_amounts)
                data["currency"] = "EUR"
                print(f"[EXTRACTION DEBUG] Found EUR cost (largest of {len(eur_amounts)}): {data['total_cost']}")
        
        # 5. Try GBP (£100,000)
        if not data["total_cost"]:
            gbp_matches = re.finditer(r'£\s*([\d,]+(?:\.\d{2})?)', raw_text)
            for match in gbp_matches:
                try:
                    cost_val = float(match.group(1).replace(",", ""))
                    if cost_val > 1000:
                        data["total_cost"] = cost_val
                        data["currency"] = "GBP"
                        print(f"[EXTRACTION DEBUG] Found GBP cost: {cost_val}")
                        break
                except:
                    pass
        
        # 6. Generic: "100000 USD" or "100000 EUR"
        if not data["total_cost"]:
            generic_matches = re.finditer(r'([\d,]+)\s+(USD|EUR|GBP|INR|AUD|CAD|CHF)', raw_text, re.IGNORECASE)
            for match in generic_matches:
                try:
                    cost_val = float(match.group(1).replace(",", ""))
                    currency_code = match.group(2).upper()
                    if cost_val > 1000:  # Reasonable amount
                        data["total_cost"] = cost_val
                        data["currency"] = currency_code
                        print(f"[EXTRACTION DEBUG] Found {currency_code} cost: {cost_val}")
                        break
                except:
                    pass
        
        # ===== TIMELINE EXTRACTION =====
        # Strategy: Find the main project phase, not ongoing/support activities
        # Extract all week numbers and identify the main project end point
        week_numbers = [int(w) for w in re.findall(r'Week\s*(\d+)', raw_text, re.IGNORECASE)]
        
        if week_numbers:
            # Look for patterns like "Week X: TVC master delivery" or similar final deliverables
            # to identify the main project completion point
            main_phase_match = re.search(
                r'Week\s*(\d+)[:\-].*?(?:TVC\s+master\s+delivery|final\s+delivery|completion|close)',
                raw_text,
                re.IGNORECASE
            )
            if main_phase_match:
                main_phase_week = int(main_phase_match.group(1))
                data["timeline_weeks"] = main_phase_week
                print(f"[EXTRACTION DEBUG] Timeline (main phase): {main_phase_week} weeks")
            else:
                # Fallback: Use approximate midpoint or look for "Phase" keywords
                # Exclude very high week numbers that are likely ongoing support
                main_weeks = [w for w in week_numbers if w <= 30]  # Main project likely < 30 weeks
                if main_weeks:
                    # Use max of main phase
                    data["timeline_weeks"] = max(main_weeks)
                    print(f"[EXTRACTION DEBUG] Timeline (filtered): {data['timeline_weeks']} weeks")
                else:
                    # If all weeks are > 30, probably ongoing support model
                    data["timeline_weeks"] = min(week_numbers)
                    print(f"[EXTRACTION DEBUG] Timeline (minimum): {data['timeline_weeks']} weeks")
        else:
            # Fallback: look for duration patterns
            duration_match = re.search(r'(?:approximately|about|total)\s+(\d+)\s+weeks?', raw_text, re.IGNORECASE)
            if duration_match:
                data["timeline_weeks"] = int(duration_match.group(1))
            else:
                # Last resort: look for "Project Duration" or similar
                duration_explicit = re.search(r'(?:Project\s+)?Duration[:\s]+(\d+)\s+weeks', raw_text, re.IGNORECASE)
                if duration_explicit:
                    data["timeline_weeks"] = int(duration_explicit.group(1))
        
        # ===== SCOPE COVERAGE EXTRACTION =====
        # Extract all "Lot N" items
        lot_matches = re.findall(r'Lot\s*(\d+)[:\s]+(.*?)(?:\n|$)', raw_text, re.IGNORECASE)
        if lot_matches:
            data["scope_coverage"] = [item[1].strip()[:80] for item in lot_matches[:8]]
            print(f"[EXTRACTION DEBUG] Scope items: {len(lot_matches)}")
        
        print(f"[EXTRACTION DEBUG] Extraction complete: {data['vendor_name']}, {data['total_cost']} {data['currency']}")
        return data
        
    except Exception as e:
        print(f"[EXTRACTION ERROR] Fallback extraction error: {e}")
        return {"error": f"Fallback extraction failed: {str(e)}"}

def extract_structured_data(raw_text):
    """Extract structured data - process ENTIRE document with AI fallback"""
    if not raw_text or len(raw_text.strip()) < 100:
        print("[EXTRACTION] No text to extract")
        return fallback_extraction(raw_text if raw_text else "")
    
    try:
        print(f"[EXTRACTION] AI extraction attempt on {len(raw_text)} chars")
        
        # Build extraction context - include ALL key sections
        extraction_text = ""
        
        # Header section (first 1500 chars)
        extraction_text += raw_text[:1500] + "\n\n"
        
        # Try to find financial/cost sections
        for pattern in [r'(?:Consolidated|Summary|TOTAL|PROJECT FEE).{0,2500}', 
                       r'(?:Commercial|Pricing|Cost|Fee).{0,2500}']:
            match = re.search(pattern, raw_text, re.IGNORECASE | re.DOTALL)
            if match:
                extraction_text += f"\n[FINANCIAL DATA]\n{match.group(0)[:2500]}\n"
        
        # Try to find timeline section
        timeline_match = re.search(r'(?:Timeline|Delivery|Milestone).{0,2000}', raw_text, re.IGNORECASE | re.DOTALL)
        if timeline_match:
            extraction_text += f"\n[TIMELINE]\n{timeline_match.group(0)[:2000]}\n"
        
        # Try to find scope/deliverables section
        scope_match = re.search(r'(?:Scope|Deliverable|Lot\s*\d+).{0,2000}', raw_text, re.IGNORECASE | re.DOTALL)
        if scope_match:
            extraction_text += f"\n[SCOPE]\n{scope_match.group(0)[:2000]}\n"
        
        # Limit total context to reasonable size
        extraction_text = extraction_text[:5000]
        
        # Try with lighter tinyllama model
        response = openai.ChatCompletion.create(
            model="llama3:latest",
            messages=[
                {
                    "role": "user", 
                    "content": f"""Extract vendor proposal data as valid JSON ONLY. Return ONLY the JSON object, no markdown, no explanation.

Return JSON object with these EXACT fields:
{{
  "vendor_name": "string (company name from header)",
  "total_cost": number (total project cost as number, remove commas/symbols),
  "currency": "string (USD|INR|EUR|GBP|AUD|CAD)",
  "timeline_weeks": number (total weeks),
  "scope_coverage": array of strings,
  "key_terms": array of strings
}}

DOCUMENT EXCERPT:
{extraction_text}"""
                }
            ],
            timeout=30
        )
        
        result_text = clean_json(response["choices"][0]["message"]["content"])
        print(f"[EXTRACTION] AI response: {result_text[:200]}")
        result = json.loads(result_text)
        
        # Validate result has required fields
        if not result.get("vendor_name"):
            result["vendor_name"] = extract_vendor_name_from_header(raw_text)
        
        print(f"[EXTRACTION] AI extracted: {result.get('vendor_name')}, {result.get('total_cost')} {result.get('currency')}")
        return result
        
    except json.JSONDecodeError as e:
        print(f"[EXTRACTION] JSON parse error: {e}, using fallback")
        return fallback_extraction(raw_text)
    except Exception as e:
        print(f"[EXTRACTION] AI extraction failed ({type(e).__name__}): {e}, using fallback")
        return fallback_extraction(raw_text)