import json
import os

import requests

ZENODO_TOKEN = os.environ.get("ZENODO_TOKEN")
if not ZENODO_TOKEN:
    print("ZENODO_TOKEN missing")
    raise SystemExit(2)
headers = {
    "Authorization": f"Bearer {ZENODO_TOKEN}",
    "Content-Type": "application/json",
}

dep_id = 18652764
print("PUT files.enabled = false for deposit", dep_id)
r = requests.put(
    f"https://zenodo.org/api/deposit/depositions/{dep_id}",
    headers=headers,
    json={"files": {"enabled": False}},
)
print("PUT status", r.status_code)
print(r.text)
print("Attempting publish")
r2 = requests.post(
    f"https://zenodo.org/api/deposit/depositions/{dep_id}/actions/publish",
    headers={"Authorization": f"Bearer {ZENODO_TOKEN}"},
)
print("publish status", r2.status_code)
try:
    print(json.dumps(r2.json(), indent=2))
except Exception:
    print(r2.text)
