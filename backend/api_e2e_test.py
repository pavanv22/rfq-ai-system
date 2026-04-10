#!/usr/bin/env python3
"""End-to-end vendor upload test via API"""
import requests
import json
import time

API_BASE = "http://localhost:8001"

print("=" * 80)
print("END-TO-END VENDOR UPLOAD TEST VIA API")
print("=" * 80)

# Test 1: Create RFQ
print("\n1️⃣ Creating RFQ via API...")
try:
    rfq_payload = {
        "project_name": "IT Infrastructure Upgrade",
        "budget": 500000,
        "currency": "USD",
        "timeline_weeks": 8,
        "sourcing_type": "RFQ",
        "scope": "Network upgrade with security",
        "requirements": [],
        "line_items": []
    }
    resp = requests.post(f"{API_BASE}/rfq/", json=rfq_payload, timeout=10)
    if resp.status_code == 201:
        rfq_data = resp.json()
        rfq_id = rfq_data["id"]
        print(f"✅ RFQ created: {rfq_id[:12]}...")
    else:
        print(f"❌ Failed: {resp.status_code} - {resp.text}")
        exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# Test 2: Upload all vendor files
vendors_to_test = [
    ("vendor_01_techcore.txt", "TechCore Solutions"),
    ("vendor_02_cloudfirst.txt", "CloudFirst Systems"),
    ("vendor_03_india_incomplete.txt", "SecureNet India"),
]

print(f"\n2️⃣ Uploading {len(vendors_to_test)} vendor files...")
for filename, expected_name in vendors_to_test:
    file_path = f"c:/Users/pavan/apps-pavan/rfq-ai-system/test_vendors/{filename}"
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (filename, f)}
            resp = requests.post(
                f"{API_BASE}/vendor/{rfq_id}/upload",
                files=files,
                timeout=120
            )
        
        if resp.status_code == 201:
            data = resp.json()
            vendor_name = data.get("vendor_name", "Unknown")
            status = data.get("extraction_status")
            print(f"   ✅ {filename}: {vendor_name} ({status})")
        else:
            print(f"   ❌ {filename}: {resp.status_code}")
    except Exception as e:
        print(f"   ❌ {filename}: {str(e)[:50]}")

# Test 3: Retrieve vendors
print(f"\n3️⃣ Retrieving vendors for RFQ...")
try:
    resp = requests.get(f"{API_BASE}/vendor/rfq/{rfq_id}", timeout=10)
    if resp.status_code == 200:
        vendors = resp.json()
        if isinstance(vendors, list):
            print(f"✅ Found {len(vendors)} vendor(s):")
            for v in vendors:
                print(f"   - {v.get('vendor_name')}: ${v.get('total_cost_usd', 'N/A')} USD")
        else:
            print(f"⚠️ Response format unexpected: {type(vendors)}")
    else:
        print(f"❌ Failed: {resp.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 4: Run scoring
print(f"\n4️⃣ Running scoring...")
try:
    score_payload = {
        "price_weight": 0.4,
        "delivery_weight": 0.3,
        "compliance_weight": 0.3
    }
    resp = requests.post(
        f"{API_BASE}/analysis/score/{rfq_id}",
        json=score_payload,
        timeout=120
    )
    if resp.status_code == 200:
        score_data = resp.json()
        print(f"✅ Scoring completed")
        print(f"   Scores: {len(score_data.get('scores', []))} vendor scores")
    else:
        print(f"⚠️ Score status: {resp.status_code}")
except Exception as e:
    print(f"⚠️ Scoring error: {str(e)[:50]}")

print("\n" + "=" * 80)
print("✅ END-TO-END TEST COMPLETE")
print("=" * 80)
