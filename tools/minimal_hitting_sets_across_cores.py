#!/usr/bin/env python3
"""Compute minimal hitting sets across selected unsat cores.

By default it selects entries in artifacts/sign_unsat_cores.json whose file name
starts with 'opt_mapping' (the problematic opt mappings) and computes all
minimal hitting sets up to a given max_size (default 3). Results are written to
artifacts/minimal_hitting_sets_across_cores.json and a small markdown report.
"""
from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path
from typing import List, Tuple

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts"
SUNC = ART / "sign_unsat_cores.json"
OUT = ART / "minimal_hitting_sets_across_cores.json"
OUT_MD = ART / "minimal_hitting_sets_across_cores.md"

if not SUNC.exists():
    print("Missing:", SUNC)
    raise SystemExit(1)

suns = json.loads(SUNC.read_text(encoding="utf-8"))
cores = [
    e
    for e in suns
    if (not e.get("solvable", False)) and e.get("file", "").startswith("opt_mapping")
]
if not cores:
    print("No opt_mapping cores found in sign_unsat_cores.json")
    raise SystemExit(1)

# Convert each core to a set of tuple(triad)
core_sets = [set(tuple(sorted(tuple(t))) for t in e["certificate_rows"]) for e in cores]
core_names = [e["file"] for e in cores]

# union of triads
union = sorted(set().union(*core_sets))
print(f"Union size: {len(union)} triads")

max_size = 3
found = []  # list of (size, [triads list])

# enumerate candidate hitting sets by size
for k in range(1, max_size + 1):
    for comb in combinations(union, k):
        ok = True
        for cs in core_sets:
            if set(comb).isdisjoint(cs):
                ok = False
                break
        if not ok:
            continue
        # check minimality: no proper subset of comb should be already found
        minimal = True
        for smaller in found:
            if set(smaller[1]).issubset(comb):
                minimal = False
                break
        if minimal:
            found.append((k, list(comb)))
    if found:
        # we've found minimal hitting sets at size k; don't search larger sizes
        break

out = {
    "cores": [{"file": c, "size": len(cs)} for c, cs in zip(core_names, core_sets)],
    "union_size": len(union),
    "minimal_hitting_sets": (
        [
            {"size": k, "hitting_sets": hs}
            for k, hs in [(found[0][0], [x[1] for x in found if x[0] == found[0][0]])]
        ]
        if found
        else []
    ),
}
OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

# small md
lines = ["# Minimal hitting sets across opt mapping cores", ""]
lines.append(f"Cores: {', '.join(core_names)}")
lines.append(f"Union size: {len(union)}")
if out["minimal_hitting_sets"]:
    m = out["minimal_hitting_sets"][0]
    lines.append(f"\nMinimal hitting sets (size {m['size']}):")
    for hs in m["hitting_sets"]:
        lines.append(f"- {hs}")
else:
    lines.append("No hitting sets found up to size 3")

OUT_MD.write_text("\n".join(lines), encoding="utf-8")
print("Wrote", OUT, "and", OUT_MD)
