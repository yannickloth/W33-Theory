#!/usr/bin/env python3
import json
from pathlib import Path

s = json.load(
    open("artifacts/e6_cubic_sign_gauge_solution.json", "r", encoding="utf-8")
)
d = [tuple(sorted(t["triple"])) for t in s["solution"]["d_triples"] if t["sign"] < 0]
print("D_BIT==1 triads count:", len(d))
print(d)
