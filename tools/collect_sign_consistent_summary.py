#!/usr/bin/env python3
import glob
import json

files = sorted(glob.glob("artifacts/sign_consistent_mapping_W*.json"))
summary = []
for f in files:
    data = json.load(open(f, "r", encoding="utf-8"))
    summary.append(
        {
            "file": f,
            "W_idx": data["W_idx"],
            "matched": data["matched"],
            "status": data["status"],
        }
    )
open("artifacts/sign_consistent_summary.json", "w", encoding="utf-8").write(
    json.dumps(summary, indent=2)
)
print("Wrote artifacts/sign_consistent_summary.json with", len(summary), "entries")
