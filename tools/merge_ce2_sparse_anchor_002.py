"""Merge candidate anchor a=(0,0,2) CE2 entries into the sparse CE2 artifact."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPARSE = ROOT / "committed_artifacts" / "ce2_sparse_local_solutions.json"
CAND = ROOT / "committed_artifacts" / "ce2_anchor_002_candidates.json"

if not SPARSE.exists() or not CAND.exists():
    raise SystemExit("Missing required sparse or candidate CE2 files")

with SPARSE.open("r", encoding="utf-8") as f:
    sparse = json.load(f)

with CAND.open("r", encoding="utf-8") as f:
    cand = json.load(f)

entries = sparse.get("entries", [])
existing_keys = {rec.get("k") for rec in entries if isinstance(rec, dict)}

added = 0
for k, v in cand.items():
    if k in existing_keys:
        continue

    def to_sparse_list(rats):
        out = []
        for idx, val in enumerate(rats):
            if val is None or val == "None" or val == "0":
                continue
            out.append([idx, str(val)])
        return out

    U_list = to_sparse_list(v.get("U_rats", []))
    V_list = to_sparse_list(v.get("V_rats", []))

    entries.append(
        {
            "k": k,
            "a": v["a"],
            "b": v["b"],
            "c": v["c"],
            "U": U_list,
            "V": V_list,
        }
    )
    added += 1

if added:
    sparse["entries"] = entries
    SPARSE.write_text(json.dumps(sparse, indent=2), encoding="utf-8")
    print(f"Added {added} entries to sparse CE2 artifact.")
else:
    print("No new entries added; all candidates already present.")
