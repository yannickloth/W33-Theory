#!/usr/bin/env python3
import glob
import json
from collections import Counter

files = glob.glob("checks/PART_CVII_e8_bijection_local_seed_*.json")
res = {}
for f in files:
    j = json.load(open(f, encoding="utf-8"))
    res[f] = j.get("status")
print("summary:")
print(Counter(res.values()))
for k, v in res.items():
    if v in ("INFEASIBLE", "OPTIMAL", "FEASIBLE"):
        print(k, v)
