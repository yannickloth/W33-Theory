#!/usr/bin/env python3
import csv
from pathlib import Path

ART = Path(__file__).resolve().parents[1]
# load cores
import json

cores = json.load(open(ART / "artifacts" / "sign_unsat_cores.json"))
# load v23 enriched
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
            rows[(u, v, w)] = r
            rows[tuple(sorted((u, v, w)))] = r
        except Exception:
            continue

for entry in cores:
    print("\nCore from", entry["file"])
    for idx, tri in enumerate(entry["unsat_core"]):
        t = tuple(sorted(tri))
        dbit = None
        import json

        d = json.load(
            open(ART / "artifacts" / "e6_cubic_sign_gauge_solution.json", "r")
        )
        d_map = {
            tuple(sorted(t["triple"])): 0 if t["sign"] == 1 else 1
            for t in d["solution"]["d_triples"]
        }
        dbit = d_map.get(t, 0)
        if t in rows:
            r = rows[t]
            print(
                idx,
                t,
                "D_BIT=",
                dbit,
                "-> s3_holonomy=",
                r[5],
                "s3_type=",
                r[6],
                "fiber6_perm=",
                r[8],
            )
        else:
            print(idx, t, "D_BIT=", dbit, "-> NOT FOUND in v23_enriched_with_types.csv")
