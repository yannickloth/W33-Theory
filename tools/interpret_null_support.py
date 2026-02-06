#!/usr/bin/env python3
"""Interpret nullspace supports: map support triad indices to affine u_line groups and print patterns."""
import json
from pathlib import Path

ART = Path(__file__).resolve().parents[1] / "artifacts"
heis = json.load(
    open(ART / "e6_cubic_affine_heisenberg_model.json", "r", encoding="utf-8")
)
triads = [
    tuple(sorted(tri)) for item in heis["affine_u_lines"] for tri in item["triads"]
]
# compute u_line index for each triad
u_line_of = {}
for ui, item in enumerate(heis["affine_u_lines"]):
    for tri in item["triads"]:
        t = tuple(sorted(tri))
        idx = triads.index(t)
        u_line_of[idx] = ui

# load sign unsat cores
cores = json.load(open(ART / "sign_unsat_cores.json", "r", encoding="utf-8"))
for entry in cores:
    print("\nCore", entry["file"])
    supp = [
        i
        for i, t in enumerate(triads)
        if t in [tuple(sorted(c)) for c in entry["unsat_core"]]
    ]
    print("  support triad indices:", supp)
    ucounts = {}
    for s in supp:
        u = u_line_of[s]
        ucounts[u] = ucounts.get(u, 0) + 1
    print("  u_line counts (u_line:count):", sorted(ucounts.items()))
    print("  u_lines involved:", sorted(set(u_line_of[s] for s in supp)))
print("\nDone")
