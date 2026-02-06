#!/usr/bin/env python3
import csv
import json
from pathlib import Path

ART = Path(__file__).resolve().parents[1]
heis = json.load(open(ART / "artifacts" / "e6_cubic_affine_heisenberg_model.json"))
triples = [
    tuple(sorted(tri)) for item in heis["affine_u_lines"] for tri in item["triads"]
]
d = json.load(open(ART / "artifacts" / "e6_cubic_sign_gauge_solution.json"))
d_map = {
    tuple(sorted(t["triple"])): 0 if t["sign"] == 1 else 1
    for t in d["solution"]["d_triples"]
}
# load v23 mapping
v23 = ART / "data" / "v23_enriched_with_types.csv"
rows = {}
with open(v23, "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    for r in reader:
        if not r:
            continue
        try:
            u = int(r[0])
            v = int(r[1])
            w = int(r[2])
            rows[tuple(sorted((u, v, w)))] = r
        except Exception:
            continue

counts = {}
for t in sorted(triples):
    s3_type = (
        rows.get(t, [None, None, None, None, None, None, None])[6]
        if t in rows
        else None
    )
    dbit = d_map.get(t, 0)
    counts.setdefault((s3_type, dbit), []).append(t)

for k, v in counts.items():
    print(k, "count=", len(v))

print("\nExamples: s3_type=3cycle, dbit=0: ", counts.get(("3cycle", 0), [])[:10])
print("Examples: s3_type=id, dbit=1: ", counts.get(("id", 1), [])[:10])
