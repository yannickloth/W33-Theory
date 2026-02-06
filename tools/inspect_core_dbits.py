#!/usr/bin/env python3
import json
from pathlib import Path

ART = Path(__file__).resolve().parents[1] / "artifacts"
cores = json.load(open(ART / "sign_unsat_cores.json", "r", encoding="utf-8"))
sdata = json.load(
    open(ART / "e6_cubic_sign_gauge_solution.json", "r", encoding="utf-8")
)
d_map = {
    tuple(sorted(t["triple"])): 0 if t["sign"] == 1 else 1
    for t in sdata["solution"]["d_triples"]
}
for entry in cores:
    print("\nCore from", entry["file"])
    for tri in entry["unsat_core"]:
        print("  tri", tri, "D_BIT=", d_map.get(tuple(sorted(tri)), None))
print("\nDone")
