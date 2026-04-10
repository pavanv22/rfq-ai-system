#!/usr/bin/env python3
"""Simple sync test - directly test vendor upload without backend"""
import sys
import os

# Setup paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 80)
print("DIRECT VENDOR UPLOAD & DATABASE TEST")
print("=" * 80)

# Initialize database
print("\n1️⃣ Initializing database...")
try:
    from app.models import init_db
    init_db()
    print("✅ Database initialized")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test extraction on file
print("\n2️⃣ Testing text extraction...")
try:
    from app.services.extractor import extract_text
    test_file = r"c:\Users\pavan\apps-pavan\rfq-ai-system\test_vendors\vendor_01_techcore.txt"
    text = extract_text(test_file)
    if text:
        print(f"✅ Extracted {len(text)} characters")
        print(f"   Preview: {text[:150]}...")
    else:
        print("❌ No text extracted")
        sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test AI extraction
print("\n3️⃣ Testing AI structured extraction...")
try:
    from app.agents.extraction_agent import extract_structured_data
    data = extract_structured_data(text)
    print(f"✅ Extraction successful!")
    if "error" not in data:
        print(f"   Vendor: {data.get('vendor_name')}")
        print(f"   Cost: ${data.get('total_cost')} {data.get('currency')}")
        print(f"   Timeline: {data.get('timeline_weeks')} weeks")
    else:
        print(f"   ⚠️ Had to use fallback: {data.get('error')}")
        print(f"   Vendor: {data.get('vendor_name')}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test normalization
print("\n4️⃣ Testing currency normalization...")
try:
    from app.services.normalizer import normalize, detect_missing_fields
    normalized = normalize(data)
    print(f"✅ Normalization successful!")
    print(f"   USD Cost: ${normalized.get('total_cost_usd')}")
    print(f"   Missing fields: {normalized.get('missing_fields', [])}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Test database insert
print("\n5️⃣ Testing database insert...")
try:
    from sqlalchemy.orm import sessionmaker
    from app.models import engine, VendorModel, RFQModel
    import uuid
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Create test RFQ first
    rfq = RFQModel(
        id=str(uuid.uuid4()),
        project_name="Test Project",
        budget=500000,
        currency="USD",
        timeline_weeks=8,
        status="active",
        scope="Test"
    )
    session.add(rfq)
    session.commit()
    print(f"✅ Created RFQ: {rfq.id[:8]}")
    
    # Create vendor
    vendor = VendorModel(
        id=str(uuid.uuid4()),
        rfq_id=rfq.id,
        vendor_name=data.get('vendor_name'),
        total_cost=data.get('total_cost'),
        currency=data.get('currency'),
        total_cost_usd=normalized.get('total_cost_usd'),
        timeline_weeks=data.get('timeline_weeks'),
        raw_extracted_data=data,
        normalized_data=normalized,
        extraction_status="normalized"
    )
    session.add(vendor)
    session.commit()
    print(f"✅ Created Vendor: {vendor.vendor_name}")
    
    # Query back
    count = session.query(VendorModel).filter(VendorModel.rfq_id == rfq.id).count()
    print(f"✅ Verified: {count} vendor(s) in database for this RFQ")
    
    session.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 80)
print("✅ ALL TESTS PASSED - System is working!")
print("=" * 80)
