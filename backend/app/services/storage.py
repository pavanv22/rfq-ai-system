import json
import os

FILE_PATH = "data/vendors.json"

def save_vendor_data(data):
    if not os.path.exists(FILE_PATH):
        with open(FILE_PATH, "w") as f:
            json.dump([], f)

    with open(FILE_PATH, "r") as f:
        existing = json.load(f)

    existing.append(data)

    with open(FILE_PATH, "w") as f:
        json.dump(existing, f, indent=2)


def load_vendor_data():
    if not os.path.exists(FILE_PATH):
        return []

    with open(FILE_PATH, "r") as f:
        return json.load(f)