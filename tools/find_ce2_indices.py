#!/usr/bin/env python3
"""Locate CE2 entries that have nonzero flattened entries at specified indices."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ce2 = json.loads((ROOT / "artifacts" / "ce2_rational_local_solutions.json").read_text())
indices = [179, 399, 581]
found = {i: [] for i in indices}
for k, e in ce2.items():
    V = e.get("V_rats", [])
    for i in indices:
        if i < len(V) and V[i] != "0":
            found[i].append((k, V[i]))

for i in indices:
    print("index", i, "found_count=", len(found[i]))
    if found[i]:
        for entry in found[i][:10]:
            print(" ", entry)
