import json
import os

import requests

ZENODO_TOKEN = os.environ.get("ZENODO_TOKEN")
if not ZENODO_TOKEN:
    print("ZENODO_TOKEN missing")
    raise SystemExit(2)
headers = {"Authorization": f"Bearer {ZENODO_TOKEN}"}
resp = requests.post(
    "https://zenodo.org/api/deposit/depositions/18652764/actions/publish",
    headers=headers,
)
print("status", resp.status_code)
try:
    print(json.dumps(resp.json(), indent=2))
except Exception:
    print(resp.text)
