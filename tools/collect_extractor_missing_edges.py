#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path("analysis/minimal_commutator_cycles")
missing = set()
for i in range(4):
    p = ROOT / f"e8_det1_combined_a2_{i}" / "e8_rootword_cocycle.json"
    if not p.exists():
        continue
    j = json.loads(p.read_text(encoding="utf-8"))
    for r in j.get("rows", []):
        if r.get("reason") == "missing_edge_root":
            me = r.get("missing_edge")
            if me:
                missing.add(me)
print("Unique missing oriented edges across A2s:")
for m in sorted(missing):
    print(m)
