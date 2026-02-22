#!/usr/bin/env python3
"""Create + publish a Zenodo deposition WITHOUT uploading release assets.
Used for cases where token cannot upload files but can create/publish metadata.
This script is idempotent (searches for existing DOI by repo+tag).
"""
import json
import os
import sys
from urllib.parse import quote_plus

import requests

ZENODO_HOST = os.environ.get("ZENODO_HOST", "https://zenodo.org")
ZENODO_TOKEN = os.environ.get("ZENODO_TOKEN")
REPO = "wilcompute/W33-Theory"
TAG = "v2026-02-15-qec-mlut"

if not ZENODO_TOKEN:
    print("ZENODO_TOKEN not set; aborting.")
    sys.exit(2)

headers = {
    "Authorization": f"Bearer {ZENODO_TOKEN}",
    "Content-Type": "application/json",
}

# 1) search for existing record
q = quote_plus(f"https://github.com/{REPO} {TAG}")
search_url = f"https://zenodo.org/api/records/?q={q}&size=100"
print("Searching Zenodo for existing record...")
r = requests.get(search_url, timeout=30)
if r.status_code != 200:
    print("Zenodo search failed:", r.status_code, r.text[:500])
else:
    hits = r.json().get("hits", {}).get("hits", [])
    for hit in hits:
        text = json.dumps(hit)
        if TAG in text and REPO in text:
            doi = hit.get("doi") or hit.get("metadata", {}).get("doi")
            if doi:
                print("Found existing DOI:", doi)
                sys.exit(0)

# 2) create draft
print("Creating new Zenodo draft...")
resp = requests.post(
    f"{ZENODO_HOST}/api/deposit/depositions",
    headers={"Authorization": f"Bearer {ZENODO_TOKEN}"},
    json={},
)
resp.raise_for_status()
dep = resp.json()
dep_id = dep.get("id")
print("Draft id=", dep_id)

# 3) set metadata (no files)
metadata = {
    "metadata": {
        "title": "Pillar-45 — GF(3) QEC primitives + MLUT (v2026-02-15-qec-mlut)",
        "upload_type": "software",
        "publication_date": "2026-02-15",
        "creators": [{"name": "Wilj D."}],
        "description": f"Pillar-45 release (GitHub): https://github.com/{REPO}/releases/tag/{TAG}",
        "version": TAG,
        "license": "MIT",
        "related_identifiers": [
            {
                "identifier": f"https://github.com/{REPO}/releases/tag/{TAG}",
                "relation": "isSupplementTo",
                "scheme": "url",
            }
        ],
    }
}
print("Setting metadata...")
resp = requests.put(
    f"{ZENODO_HOST}/api/deposit/depositions/{dep_id}",
    headers={"Authorization": f"Bearer {ZENODO_TOKEN}"},
    json=metadata,
)
resp.raise_for_status()

# 4) publish
print("Publishing deposition...")
resp = requests.post(
    f"{ZENODO_HOST}/api/deposit/depositions/{dep_id}/actions/publish",
    headers={"Authorization": f"Bearer {ZENODO_TOKEN}"},
)
resp.raise_for_status()
pr = resp.json()
doi = pr.get("doi") or pr.get("metadata", {}).get("doi")
if doi:
    print("Published DOI:", doi)
    print("DOI URL:", f"https://doi.org/{doi}")
    sys.exit(0)
else:
    print("Publish did not return DOI, response:", pr)
    sys.exit(1)
