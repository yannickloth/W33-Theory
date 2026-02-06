#!/usr/bin/env python3
import json

m = json.load(open("artifacts/triad_label_permutation.json"))["mapping"]
inv = {int(v): int(k) for k, v in m.items()}
print("preimage of [0,18,25] =", [inv.get(0), inv.get(18), inv.get(25)])
print(
    "Which Schlaefli triangle is that (mapped to H indices):",
    sorted([inv.get(0), inv.get(18), inv.get(25)]),
)
print("preimage of [0,20,23] =", [inv.get(0), inv.get(20), inv.get(23)])
print(
    "Which Schlaefli triangle is that (mapped to H indices):",
    sorted([inv.get(0), inv.get(20), inv.get(23)]),
)
