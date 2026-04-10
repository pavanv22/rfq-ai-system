#!/usr/bin/env python3
"""Direct vendor upload test - bypass frontend"""
import requests
import json

API_BASE = "http://localhost:8000"

print("=" * 80)
print("DIRECT VENDOR UPLOAD TEST")
print("=" * 80)

# Step 1: Create RFQ
print("\n1️⃣ Creating RFQ...")
rfq_data = {
    "project_name": "Test Project",
    "budget": 500000,
    "currency": "USD",
    "timeline_weeks": 8,
    "sourcing_type": "RFQ",
    "scope": "Test vendor evaluation",
    "requirements": [],
    "line_items": []
}

try:
    resp = requests.post(f"{API_BASE}/rfq/", json=rfq_data, timeout=10)
    print(f"Status: {resp.status_code}")
    data = resp.json()
    if "id" in data and data["id"]:
        rfq_id = data["id"]
        print(f"✅ RFQ created: {rfq_id}")
    else:
        print(f"❌ Failed: {data}")
        exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# Step 2: Upload vendor file
print(f"\n2️⃣ Uploading vendor file...")
test_file = r"c:\Users\pavan\apps-pavan\rfq-ai-system\test_vendors\vendor_01_techcore.txt"

try:
    with open(test_file, 'rb') as f:
        files = {'file': f}
        url = f"{API_BASE}/vendor/{rfq_id}/upload"
        resp = requests.post(url, files=files, timeout=60)
    
    print(f"Status: {resp.status_code}")
    data = resp.json()
    print(json.dumps(data, indent=2))
    
    if resp.status_code == 201:
        print("✅ Vendor uploaded successfully!")
    else:
        print(f"❌ Upload failed: {data}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Step 3: Verify vendors in database
print(f"\n3️⃣ Checking database...")
try:
    import sqlite3
    conn = sqlite3.connect("c:/Users/pavan/apps-pavan/rfq-ai-system/backend/rfq_system.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*), vendor_name, total_cost_usd FROM vendors GROUP BY vendor_name")
    rows = c.fetchall()
    if rows:
        print(f"✅ Vendors in database:")
        for row in rows:
            print(f"   {row[1]}: ${row[2]} USD")
    else:
        print("❌ No vendors in database!")
    conn.close()
except Exception as e:
    print(f"❌ Database check failed: {e}")

print("\n" + "=" * 80)
