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
        # Look specifically for "TOTAL PROJECT FEE" line and extract number after it
        total_fee_match = re.search(
            r'TOTAL\s+PROJECT\s+FEE.*?[\r\n]\s*([\d,\.]+)',
            raw_text,
            re.IGNORECASE | re.DOTALL
        )
        if total_fee_match:
            print(f"[EXTRACTION DEBUG] Found 'TOTAL PROJECT FEE' line: {total_fee_match.group(1)}")
            return total_fee_match.group(1)
        
        # Fallback patterns
        summary_patterns = [
            r'(?:Consolidated|Summary|TOTAL).{0,200}?(?:Project Fee|Total).*?[\r\n].*?([\d,\.]+)',
            r'TOTAL PROJECT FEE.*?[\r\n].*?([\d,\.]+)',
            r'Total Agency Fees.*?[\r\n].*?([\d,\.]+)',
        ]
        
        for pattern in summary_patterns:
            match = re.search(pattern, raw_text, re.IGNORECASE | re.DOTALL)
            if match:
                print(f"[EXTRACTION DEBUG] Found summary amount via pattern: {match.group(1)}")
                return match.group(1)
        
        return None
    except Exception as e:
        print(f"[EXTRACTION DEBUG] Consolidated summary error: {e}")
        return None

def extract_vendor_name_from_header(raw_text):
    """Extract vendor/company name from document header - more flexible"""
    lines = raw_text.split('\n')
    
    # Look for company name patterns in first 30 lines
    for i, line in enumerate(lines[:30]):
        line_clean = line.strip()
        
        # Skip empty lines and very short lines
        if not line_clean or len(line_clean) < 5:
            continue
        
        # Skip common headers like "Response to:", "RFQ", "Prepared By:", etc.
        if any(skip in line_clean.lower() for skip in ["response to:", "rfq", "prepared ", "date:", "version:", "validity:"]):
            continue
        
        # Pattern: Look for company name indicators
        if any(keyword in line_clean.lower() for keyword in ["communications", "pvt", "ltd", "inc", "llc", "agency", "corp", "company"]):
            return line_clean
    
    # Fallback: Look for any capitalized phrase in first 10 lines that's not a common keyword
    for line in lines[:10]:
        line_clean = line.strip()
        if len(line_clean) > 8 and len(line_clean) < 100:
            # Check if it looks like a company name (has at least one capital letter and not all caps)
            if not line_clean.isupper() and any(c.isupper() for c in line_clean):
                if line_clean[0].isupper():
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
        # Strategy: Look for large numbers which are likely costs
        # Priority: INR > USD > EUR > GBP > Generic currency codes
        
        # 1. Try INR with both formats: "INR 3,43,37,900" or "3,43,37,900 INR"
        # Use more flexible regex to handle line breaks and spacing
        inr_matches = re.finditer(r'([\d,\.]+)\s*(?:INR|₹)', raw_text, re.IGNORECASE | re.MULTILINE)
        for match in inr_matches:
            try:
                cost_str = match.group(1)
                # Handle comma-separated numbers - remove all commas first
                cost_val = float(cost_str.replace(",", ""))
                if cost_val > 100:  # Reasonable INR amount
                    data["total_cost"] = cost_val
                    data["currency"] = "INR"
                    print(f"[EXTRACTION DEBUG] Found INR cost: {cost_str} → {cost_val}")
                    break
            except Exception as e:
                print(f"[EXTRACTION DEBUG] INR parsing error: {e}")
                pass
        
        # If no INR found, try INR symbol ₹
        if not data["total_cost"]:
            rupee_matches = re.finditer(r'₹\s*([\d,\.]+)', raw_text)
            for match in rupee_matches:
                try:
                    cost_val = float(match.group(1).replace(",", ""))
                    if cost_val > 100:
                        data["total_cost"] = cost_val
                        data["currency"] = "INR"
                        print(f"[EXTRACTION DEBUG] Found INR (₹) cost: {cost_val}")
                        break
                except:
                    pass
        
        # Try to find standalone large INR numbers (might be without explicit INR label nearby)
        if not data["total_cost"]:
            # Look for numbers > 100k that might be INR project costs
            large_numbers = re.finditer(r'\b([\d]{3,},[\d]{2},[\d]{3}|[\d]{3},[\d]{2},[\d]{3}|[\d,]+)\b', raw_text)
            for match in large_numbers:
                try:
                    num_str = match.group(1)
                    num_val = float(num_str.replace(",", ""))
                    # If we find a number > 1 million and document mentions INR, likely a cost
                    if num_val > 1000000 and "inr" in raw_text.lower() and data.get("total_cost") is None:
                        data["total_cost"] = num_val
                        data["currency"] = "INR"
                        print(f"[EXTRACTION DEBUG] Found large INR number: {num_str} → {num_val}")
                        break
                except:
                    pass
        
        # 2. Look for consolidated summary amounts (large round numbers)
        summary_amount = find_consolidated_summary(raw_text)
        if summary_amount and not data["total_cost"]:
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
        
        # 3. Try USD ($100,000)
        if not data["total_cost"]:
            usd_matches = re.finditer(r'\$\s*([\d,]+(?:\.\d{2})?)', raw_text)
            for match in usd_matches:
                try:
                    cost_val = float(match.group(1).replace(",", ""))
                    if cost_val > 1000:  # Reasonable USD amount
                        data["total_cost"] = cost_val
                        data["currency"] = "USD"
                        print(f"[EXTRACTION DEBUG] Found USD cost: {cost_val}")
                        break
                except:
                    pass
        
        # 4. Try EUR (€100,000)
        if not data["total_cost"]:
            eur_matches = re.finditer(r'€\s*([\d,]+(?:\.\d{2})?)', raw_text)
            for match in eur_matches:
                try:
                    cost_val = float(match.group(1).replace(",", ""))
                    if cost_val > 1000:
                        data["total_cost"] = cost_val
                        data["currency"] = "EUR"
                        print(f"[EXTRACTION DEBUG] Found EUR cost: {cost_val}")
                        break
                except:
                    pass
        
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
        # Get maximum week number for project duration
        week_numbers = [int(w) for w in re.findall(r'Week\s*(\d+)', raw_text, re.IGNORECASE)]
        if week_numbers:
            data["timeline_weeks"] = max(week_numbers)
            print(f"[EXTRACTION DEBUG] Timeline: {data['timeline_weeks']} weeks")
        else:
            # Fallback: look for duration patterns
            duration_match = re.search(r'(?:approximately|about|total)\s+(\d+)\s+weeks?', raw_text, re.IGNORECASE)
            if duration_match:
                data["timeline_weeks"] = int(duration_match.group(1))
        
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