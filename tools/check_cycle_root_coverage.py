#!/usr/bin/env python3
import json

cycles = json.load(
    open(
        "analysis/minimal_commutator_cycles/minimal_holonomy_cycles_ordered_rootwords.json"
    )
)
e2 = json.load(open("artifacts/edge_root_bijection_canonical.json"))
# build mapping set of edges
e_set = set()
for d in e2:
    a = int(d["v_i"])
    b = int(d["v_j"])
    e_set.add((a, b))
    e_set.add((b, a))
# check coverage
full = 0
total = 0
covered = []
for c in cycles:
    cyc = list(map(int, c["cycle_vertices"].split(",")))
    edges = [(cyc[i], cyc[(i + 1) % len(cyc)]) for i in range(len(cyc))]
    total += 1
    if all(e in e_set for e in edges):
        full += 1
        covered.append(c)
print("cycles total", total, "fully_mapped", full)
for i, c in enumerate(covered[:10]):
    print(i, c["id"], c["k"], c["cycle_vertices"])
