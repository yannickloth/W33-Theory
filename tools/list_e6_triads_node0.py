#!/usr/bin/env python3
"""List E6 triads containing node 0 with D_BIT and S3 holonomy info."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts"

# load e6 triads (affine + fiber)
e6 = json.load(open(ART / "e6_cubic_sign_gauge_solution.json", "r", encoding="utf-8"))
# d_map
d_map = {
    tuple(sorted(t["triple"])): 0 if t["sign"] == 1 else 1
    for t in e6["solution"]["d_triples"]
}
# load affine+fiber
heis = json.load(
    open(ART / "e6_cubic_affine_heisenberg_model.json", "r", encoding="utf-8")
)
E6_triads = [
    tuple(sorted(tri)) for item in heis["affine_u_lines"] for tri in item["triads"]
] + [tuple(sorted(t)) for t in heis["fiber_triads_e6id"]]

# load v23 CSV
csvp = ROOT / "data" / "v23_enriched_with_types.csv"
rows = {}
with open(csvp, "r", encoding="utf-8") as f:
    r = csv.reader(f)
    for row in r:
        if not row:
            continue
        try:
            u = int(row[0])
            v = int(row[1])
            w = int(row[2])
            rows[tuple(sorted((u, v, w)))] = row
        except Exception:
            continue

for tri in sorted(set(E6_triads)):
    if 0 in tri:
        dbit = d_map.get(tri, None)
        r = rows.get(tri)
        hol = r[5] if r else None
        typ = r[6] if r else None
        print(tri, "D_BIT=", dbit, "s3_holonomy=", hol, "s3_type=", typ)
