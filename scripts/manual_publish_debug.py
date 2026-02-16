import os

import requests

ZENODO_TOKEN = os.environ.get("ZENODO_TOKEN")
if not ZENODO_TOKEN:
    print("ZENODO_TOKEN missing")
    raise SystemExit(2)
url = "https://zenodo.org/api/deposit/depositions/18652764/actions/publish"
headers = {"Authorization": f"Bearer {ZENODO_TOKEN}"}
print("POST", url)
resp = requests.post(url, headers=headers)
print("status:", resp.status_code)
print("headers:", resp.headers)
print("text:", resp.text)
