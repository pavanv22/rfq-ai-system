import requests, sys
BASE='http://127.0.0.1:8001'

try:
    r = requests.get(f"{BASE}/rfq/")
    r.raise_for_status()
    rfqs = r.json()
    if not rfqs:
        print('No RFQs found')
        sys.exit(1)
    # pick first RFQ that has vendors
    rfq_id = None
    for rfq in rfqs:
        vid_resp = requests.get(f"{BASE}/vendor/rfq/{rfq.get('id')}")
        if vid_resp.status_code == 200:
            vendors = vid_resp.json()
            if vendors:
                rfq_id = rfq.get('id')
                print('Selected RFQ with vendors:', rfq_id)
                break
    if not rfq_id:
        print('No RFQ with vendors found')
        sys.exit(1)

    # Run scoring
    print('Running scoring...')
    resp = requests.post(f"{BASE}/analysis/{rfq_id}/score")
    print('Score response status:', resp.status_code)
    try:
        print(resp.json())
    except Exception as e:
        print('Score response text:', resp.text)

    # Generate recommendation
    print('Generating recommendation...')
    resp = requests.post(f"{BASE}/analysis/{rfq_id}/recommend")
    print('Recommend response status:', resp.status_code)
    try:
        print(resp.json())
    except Exception as e:
        print('Recommend response text:', resp.text)

except Exception as e:
    print('Error during test:', e)
    sys.exit(2)
