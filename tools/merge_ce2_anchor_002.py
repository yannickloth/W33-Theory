"""Merge candidate CE2 local solutions for anchor a=(0,0,2) into the committed artifact."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts" / "ce2_rational_local_solutions.json"
CAND = ROOT / "committed_artifacts" / "ce2_anchor_002_candidates.json"

if not ART.exists() or not CAND.exists():
    raise SystemExit("Missing required artifact files")

with ART.open("r", encoding="utf-8") as f:
    ce2 = json.load(f)

with CAND.open("r", encoding="utf-8") as f:
    cand = json.load(f)

added = 0
for k, v in cand.items():
    if k in ce2:
        continue
    entry = {
        "a": v["a"],
        "b": v["b"],
        "c": v["c"],
        "types": ["g1", "g1", "g2"],
        "U_norm": v.get("U_norm", 0.0),
        "V_norm": v.get("V_norm", 0.0),
        "U_rats": v.get("U_rats", []),
        "V_rats": v.get("V_rats", []),
        "W_rats": ["0"] * 900,
    }
    ce2[k] = entry
    added += 1

if added:
    ART.write_text(json.dumps(ce2, indent=2), encoding="utf-8")
    print(f"Added {added} new CE2 entries for anchor a=(0,0,2)")
else:
    print("No new entries added; all candidates already present.")
