import json
import os
import sys

import requests

ZENODO_TOKEN = os.environ.get("ZENODO_TOKEN")
if not ZENODO_TOKEN:
    print("ZENODO_TOKEN missing")
    sys.exit(2)
headers = {"Authorization": f"Bearer {ZENODO_TOKEN}"}
for dep_id in ("18652758", "18652764"):
    r = requests.get(
        f"https://zenodo.org/api/deposit/depositions/{dep_id}", headers=headers
    )
    print("\nDEPOSIT", dep_id, "status", r.status_code)
    try:
        print(json.dumps(r.json(), indent=2)[:4000])
    except Exception as e:
        print("failed to parse json", e)
