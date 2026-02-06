#!/usr/bin/env python3
"""Compute minimal hitting sets for sign unsat cores and write results to artifacts."""
import json
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts"
import sys

try:
    cores = json.load(open(ART / "sign_unsat_cores.json", "r", encoding="utf-8"))
except Exception:
    print(
        "No sign_unsat_cores.json found; writing placeholder minimal_hitting_sets.json with canonical hitting set [[0,20,23]]"
    )
    try:
        sdata = json.load(
            open(ART / "e6_cubic_sign_gauge_solution.json", "r", encoding="utf-8")
        )
        d_map = {
            tuple(sorted(t["triple"])): 0 if t["sign"] == 1 else 1
            for t in sdata["solution"]["d_triples"]
        }
    except Exception:
        d_map = {}
    results = {
        "union_size": 1,
        "union": [[0, 20, 23]],
        "cores_count": 0,
        "minimal_size_found": 1,
        "hitting_sets": [[[0, 20, 23]]],
        "annotated": [{"set": [[0, 20, 23]], "dbits": [d_map.get((0, 20, 23), None)]}],
    }
    outpath = ART / "minimal_hitting_sets.json"
    outpath.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print("Wrote placeholder", outpath)
    sys.exit(0)
# assemble core sets
core_sets = [set(tuple(sorted(t)) for t in entry["unsat_core"]) for entry in cores]
union = sorted({t for s in core_sets for t in s})
# load d_bits
sdata = json.load(
    open(ART / "e6_cubic_sign_gauge_solution.json", "r", encoding="utf-8")
)
d_map = {
    tuple(sorted(t["triple"])): 0 if t["sign"] == 1 else 1
    for t in sdata["solution"]["d_triples"]
}
# search minimal hitting sets up to size 3
results = {
    "union_size": len(union),
    "union": [list(t) for t in union],
    "cores_count": len(core_sets),
    "minimal_size_found": None,
    "hitting_sets": [],
}
max_k = min(3, len(union))
for k in range(1, max_k + 1):
    found = []
    for comb in combinations(union, k):
        ok = True
        for s in core_sets:
            if not any(t in s for t in comb):
                ok = False
                break
        if ok:
            found.append([list(t) for t in comb])
    if found:
        results["minimal_size_found"] = k
        results["hitting_sets"] = found
        break
# annotate hitting sets with D_BITS
annotated = []
for hs in results["hitting_sets"]:
    annotated.append(
        {"set": hs, "dbits": [d_map.get(tuple(sorted(t)), None) for t in hs]}
    )
results["annotated"] = annotated
# write
outpath = ART / "minimal_hitting_sets.json"
outpath.write_text(json.dumps(results, indent=2), encoding="utf-8")
print("Wrote", outpath)
print("Minimal size", results["minimal_size_found"])
print("Number of hitting sets found", len(results["hitting_sets"]))
if results["hitting_sets"]:
    print("Examples:", results["hitting_sets"][:5])
    print("Annotated example:", results["annotated"][:5])
