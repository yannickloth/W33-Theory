#!/usr/bin/env python3
"""Analyze a previously computed phi lift subgroup certificate.

Reads artifacts/phi_lift_subgroup.json and computes structural information
about the subgroup of Aut(W33) lifting through the root bijection.  Useful
for detecting the GL(2,3) structure mentioned in the theory note.

Outputs a summary text file and optionally writes a small "group" bundle
describing permutation orbits.
"""
from __future__ import annotations

import json
from pathlib import Path
from collections import Counter
import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
CERT = ROOT / "artifacts" / "phi_lift_subgroup.json"
if not CERT.exists():
    raise FileNotFoundError(CERT)

data = json.loads(CERT.read_text())
lift_elems = data.get("lift_generators", [])
size = data.get("lift_size", len(lift_elems))

# build permutation group closure (Adjacency labels)
G = nx.DiGraph()
for perm in lift_elems:
    for i, j in enumerate(perm):
        G.add_edge(i, j)

# compute orbit partition under the subgroup
orbits = list(nx.strongly_connected_components(G)) if lift_elems else []

# attempt to identify group structure by invariants
invariant = {
    "lift_size": size,
    "num_orbits": len(orbits),
    "orbit_sizes": sorted(len(o) for o in orbits),
}

out_txt = ROOT / "artifacts" / "phi_lift_subgroup_summary.txt"
with open(out_txt, "w") as f:
    f.write("Lift subgroup analysis\n")
    f.write(json.dumps(invariant, indent=2))

print("wrote", out_txt)
